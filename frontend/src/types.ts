export type Persona = 'fan'|'analyst'|'broadcaster';
export type Language = 'en'|'hi'|'es';
export interface Player { id:string; team_id:string; name:string; number:number; position:string; involvement:number; passes:number; completed:number; goals:number; shots:number; defensive:number; event_ids:string[] }
export interface Team { id:string; name:string; short:string; color:string; players:Player[] }
export interface Event { event_id:string; match_id:string; sequence_number:number; period:number; match_clock_ms:number; team_id:string; player_id:string; event_type:string; start_x:number; start_y:number; end_x:number; end_y:number; outcome:string; related_event_ids:string[]; event_attributes:Record<string,unknown> }
export interface Match { id:string; title:string; description:string; seed:number; home:Team; away:Team; duration_ms:number; events:Event[]; event_count?:number; provenance:string }
export interface State { match_id:string; at_ms:number; event_count:number; stats:Record<string,Record<string,number>>; players:Player[]; momentum:({minute:number}&Record<string,number>)[]; counterattacks:{team_id:string; at_ms:number; event_ids:string[]}[]; key_moments:Event[]; latest_event:Event|null; method:string }
export interface Claim { claim_id:string; team_id:string; metric:string; value:number; previous_value:number; window_start_ms:number; window_end_ms:number; source_event_ids:string[]; confidence:string; reason_code:string }
export interface Overlay { overlay_id:string; match_id:string; start_ms:number; end_ms:number; overlay_type:string; heading:string; supporting_statistic:string; source_event_ids:string[]; position:Record<string,number>; audience:Persona; language:Language; verification_status:string }
export interface Story { claim:Claim; headline:string; text:string; why:string; confidence:string; audience:Persona; language:Language; overlay:Overlay }
export interface Trace { agent:string; task:string; input_summary:string; output_summary:string; duration_ms:number; source_event_ids:string[]; validation:string; mode:string; status:string; attempts:number; errors?:string[]; raw_output?:string; tool_calls?:unknown[] }
export interface Run { run_id:string; match_id:string; at_ms:number; framework:string; provider_requested:string; favorite_team:string|null; execution_mode:string; duration_ms:number; published:Story|null; variants:Story[]; traces:Trace[]; repairs:number; status:string; recording_label?:string }
export interface Artifact { match:Match; snapshots:State[]; runs:Run[]; recovery_run:Run }
