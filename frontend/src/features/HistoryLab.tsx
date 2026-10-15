import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownToLine,
  Database,
  ExternalLink,
  ShieldCheck,
  X,
} from "lucide-react";
import { API_CONFIG } from "../services/api";

type Row = {
  id: string;
  competition: string;
  competition_name: string;
  season: string;
  date: string;
  home: string;
  away: string;
  home_goals: number | null;
  away_goals: number | null;
  played: boolean;
  cancelled?: boolean;
  source_url: string;
  license: string;
  stage: string;
  evaluation: string;
  probabilities: Record<string, number> | null;
  features: Record<string, number>;
  feature_cutoff: string;
};
type Metrics = {
  matches: number;
  accuracy: number;
  log_loss: number;
  brier: number;
};
type Summary = {
  coverage: {
    matches: number;
    scored_matches: number;
    scope: Record<string, string>;
    coverage: {
      competition: string;
      name: string;
      season: string;
      fixtures: number;
      scored_matches: number;
      expected_main_matches: number | null;
      status: string;
      cancelled: number;
    }[];
    start_date: string;
    end_date: string;
    license: string;
  };
  model: {
    name: string;
    heldout: Metrics;
    frequency_baseline: Metrics;
    splits: Record<string, number>;
    production_training_matches: number;
    limitations: string[];
  };
};
const percent = (n: number) => `${(n * 100).toFixed(1)}%`;

export function HistoryLab({ connected }: { connected: boolean }) {
  const [summary, setSummary] = useState<Summary | null>(null),
    [rows, setRows] = useState<Row[]>([]),
    [competition, setCompetition] = useState("en.1"),
    [season, setSeason] = useState("2025-26"),
    [club, setClub] = useState(""),
    [selected, setSelected] = useState<Row | null>(null),
    [page, setPage] = useState(0),
    [error, setError] = useState(""),
    [prediction, setPrediction] = useState<Record<string, number> | null>(null),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}history/summary.json`)
      .then((r) => {
        if (!r.ok)
          throw Error(
            "Historical artifacts are missing. Run python -m scripts.fetch_history and python -m scripts.train_history.",
          );
        return r.json();
      })
      .then(setSummary)
      .catch((e) => setError(String(e)));
  }, []);
  useEffect(() => {
    let active = true;
    setRows([]);
    setPage(0);
    setSelected(null);
    setPrediction(null);
    fetch(`${import.meta.env.BASE_URL}history/${competition}.json`)
      .then((r) => {
        if (!r.ok) throw Error("Historical competition file unavailable");
        return r.json();
      })
      .then((v) => {
        if (active) setRows(v);
      })
      .catch((e) => setError(String(e)));
    return () => {
      active = false;
    };
  }, [competition]);
  const filtered = useMemo(
    () =>
      rows
        .filter(
          (r) =>
            r.season === season &&
            (!club ||
              `${r.home} ${r.away}`.toLowerCase().includes(club.toLowerCase())),
        )
        .sort((a, b) => a.date.localeCompare(b.date)),
    [rows, season, club],
  );
  useEffect(() => {
    if (!selected) return;
    const previous = document.activeElement as HTMLElement | null;
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelected(null);
      if (event.key === "Tab") {
        const items = Array.from(
          document.querySelectorAll<HTMLElement>(
            ".history-lab .evidence-drawer button:not(:disabled), .history-lab .evidence-drawer a",
          ),
        );
        const first = items[0],
          last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      document.body.style.overflow = old;
      previous?.focus();
    };
  }, [selected]);
  const coverage = summary?.coverage.coverage.find(
    (r) => r.competition === competition && r.season === season,
  );
  async function rerun() {
    if (!selected || !connected || !API_CONFIG.baseURL) return;
    setBusy(true);
    try {
      const response = await fetch(
        `${API_CONFIG.baseURL}/api/history/prediction/${selected.id}`,
        { signal: AbortSignal.timeout(15000) },
      );
      if (!response.ok) throw Error("Backend model request failed");
      setPrediction((await response.json()).probabilities);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  function download() {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(filtered, null, 2)], {
        type: "application/json",
      }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = `${competition}-${season}-real-results.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 300);
  }
  if (!summary)
    return (
      <section className="panel mini-panel">
        <h2>
          <Database size={18} /> Real match lab
        </h2>
        <p role="status">
          {error ||
            "Loading actual historical results and the trained model report…"}
        </p>
      </section>
    );
  return (
    <div className="history-lab">
      <div className="history-notice">
        <ShieldCheck size={18} />
        <div>
          <strong>
            Real results. Trained result model. Separate from synthetic event
            replay.
          </strong>
          <p>
            1 Jan 2021–30 Jun 2026 · Big five + three UEFA main competitions ·
            2026–27 excluded · No pressure or player-tracking data inferred from
            scores.
          </p>
        </div>
      </div>
      <div className="history-metrics">
        {[
          [
            "Real scored matches",
            summary.coverage.scored_matches.toLocaleString(),
          ],
          [
            "Untouched 2025–26 test",
            summary.model.heldout.matches.toLocaleString(),
          ],
          ["Held-out accuracy", percent(summary.model.heldout.accuracy)],
          [
            "Frequency baseline",
            percent(summary.model.frequency_baseline.accuracy),
          ],
        ].map(([label, value]) => (
          <section className="panel" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </section>
        ))}
      </div>
      <section className="panel">
        <div className="panel-heading">
          <h2>
            <Database size={16} /> Historical match explorer
          </h2>
          <button className="text-button" onClick={download}>
            <ArrowDownToLine size={14} /> Export filtered data
          </button>
        </div>
        <div className="history-filters">
          <label>
            Competition
            <select
              aria-label="Real competition"
              value={competition}
              onChange={(e) => {
                setCompetition(e.target.value);
                setPage(0);
              }}
            >
              {Object.entries(summary.coverage.scope).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Season
            <select
              aria-label="Historical season"
              value={season}
              onChange={(e) => {
                setSeason(e.target.value);
                setPage(0);
              }}
            >
              {[
                "2025-26",
                "2024-25",
                "2023-24",
                "2022-23",
                "2021-22",
                "2020-21",
              ].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>
            Find a club
            <input
              aria-label="Historical club filter"
              placeholder="Arsenal, Barcelona…"
              value={club}
              onChange={(e) => {
                setClub(e.target.value);
                setPage(0);
              }}
            />
          </label>
        </div>
        <p className="history-coverage">
          {coverage
            ? `${coverage.scored_matches} scored / ${coverage.expected_main_matches ?? "date-windowed"} expected · ${coverage.status} · ${coverage.cancelled || 0} cancelled`
            : "No season data available."}{" "}
          {season === "2020-21"
            ? "Only fixtures from January 2021 onward are included."
            : ""}{" "}
          Completion is by fixture count, not independent certification of every
          score.
        </p>
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Home</th>
                <th>90′ score</th>
                <th>Away</th>
                <th>Home / draw / away estimate</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(page * 30, (page + 1) * 30).map((row) => (
                <tr key={row.id}>
                  <td>{row.date}</td>
                  <td>{row.home}</td>
                  <td>
                    <button
                      aria-label={`Inspect ${row.home} vs ${row.away} on ${row.date}`}
                      onClick={() => {
                        setSelected(row);
                        setPrediction(null);
                      }}
                    >
                      {row.played
                        ? `${row.home_goals} – ${row.away_goals}`
                        : row.cancelled
                          ? "Cancelled"
                          : "Unscored"}
                    </button>
                  </td>
                  <td>{row.away}</td>
                  <td>
                    {row.probabilities ? (
                      <div className="probability-bar" title={row.evaluation}>
                        {Object.entries(row.probabilities).map(
                          ([key, value]) => (
                            <span
                              className={key}
                              key={key}
                              style={{ width: `${value * 100}%` }}
                            >
                              {Math.round(value * 100)}%
                            </span>
                          ),
                        )}
                      </div>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <a
                      href={row.source_url}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`Source for ${row.home} vs ${row.away}`}
                    >
                      <ExternalLink size={13} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!filtered.length && (
          <p className="empty">
            {rows.length
              ? "No fixtures match this selection."
              : "Loading competition results…"}
          </p>
        )}
        <div className="history-pages">
          <span>
            {filtered.length} fixtures · page{" "}
            {Math.min(page + 1, Math.max(1, Math.ceil(filtered.length / 30)))}/
            {Math.max(1, Math.ceil(filtered.length / 30))}
          </span>
          <button disabled={!page} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <button
            disabled={(page + 1) * 30 >= filtered.length}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      </section>
      <div className="two-grid">
        <section className="panel mini-panel">
          <h2>What was actually trained?</h2>
          <p>
            Multinomial logistic regression fitted on real, pre-match
            rating/form/rest features. Training: Jan 2021–Jun 2024.
            Hyperparameters: Jul 2024–Jun 2025 validation. Evaluation weights
            use data strictly before Jul 2025. The complete 2025–26 season is
            held out from fitting.
          </p>
          <p>
            Test log loss:{" "}
            <strong>{summary.model.heldout.log_loss.toFixed(3)}</strong> versus
            baseline{" "}
            <strong>
              {summary.model.frequency_baseline.log_loss.toFixed(3)}
            </strong>
            . Brier score: {summary.model.heldout.brier.toFixed(3)}. Scores are
            observations; probabilities are fallible model estimates.
          </p>
          <p>
            Earlier seasons show training/validation-period estimates, not
            held-out performance. Form updates only after each match day;
            weights stay fixed during the holdout. This trains a result model,
            not the local language model.
          </p>
          <p>
            A separate production model is refitted on all{" "}
            {summary.model.production_training_matches.toLocaleString()}{" "}
            completed matches through June 2026. Its retrospective in-sample
            predictions are not used for the reported test scores.
          </p>
        </section>
        <section className="panel mini-panel">
          <h2>Coverage you can inspect</h2>
          <div className="coverage-grid">
            {summary.coverage.coverage
              .filter((c) => c.season === season)
              .map((c) => (
                <div key={c.competition}>
                  <span>{c.name}</span>
                  <strong>
                    {c.scored_matches}/{c.expected_main_matches ?? "window"}
                  </strong>
                  <small>{c.status}</small>
                </div>
              ))}
          </div>
          <p className="small muted">
            OpenFootball data: CC0. Wikipedia supplements: CC BY-SA 4.0 with
            revision links and contributor attribution. Combined historical data
            and model artifacts: CC BY-SA 4.0. No club logos or footage.
          </p>
        </section>
      </div>
      {error && (
        <p role="status" className="warning-note">
          {error}
        </p>
      )}
      {selected && (
        <div className="drawer-backdrop" onClick={() => setSelected(null)}>
          <aside
            className="evidence-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Real match details"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-header">
              <span>Actual match · source and estimate</span>
              <button
                autoFocus
                aria-label="Close real match details"
                onClick={() => setSelected(null)}
              >
                <X size={19} />
              </button>
            </div>
            <h2>
              {selected.home} vs {selected.away}
            </h2>
            <p>
              {selected.date} · {selected.competition_name} {selected.season}
            </p>
            <div className="evidence-value">
              {selected.played
                ? `${selected.home_goals}–${selected.away_goals}`
                : selected.cancelled
                  ? "Cancelled"
                  : "Unscored"}
              <span>Regulation-time result · {selected.evaluation}</span>
            </div>
            <p>
              Model features use results strictly before{" "}
              {selected.feature_cutoff}. No final score is an input to this
              match's estimate.
            </p>
            <div className="history-prediction">
              {Object.entries(prediction || selected.probabilities || {}).map(
                ([key, value]) => (
                  <div key={key}>
                    <span>{key}</span>
                    <strong>{percent(value)}</strong>
                  </div>
                ),
              )}
            </div>
            <button
              className="secondary-button"
              disabled={!connected || busy || selected.cancelled}
              onClick={rerun}
            >
              {busy ? "Calculating…" : "Run trained model on backend"}
            </button>
            {!connected && (
              <p className="small muted">
                Connect the backend to recompute. The displayed estimates were
                produced by the actual trained model during artifact generation.
              </p>
            )}
            <h3>Pre-match features</h3>
            <pre>{JSON.stringify(selected.features, null, 2)}</pre>
            <p>
              <a href={selected.source_url} target="_blank" rel="noreferrer">
                Open source record ↗
              </a>
            </p>
            <p className="small muted">
              {selected.license}. Wikipedia-derived records credit the article
              contributors and linked revision history. No live match-feed or
              tactical-event analysis is claimed.
            </p>
          </aside>
        </div>
      )}
    </div>
  );
}
