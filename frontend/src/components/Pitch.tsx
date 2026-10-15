import {useId} from 'react';
import type {Event, Match} from '../types';

export function Pitch({match,events,layer='all',playerId,onEvent}:{match:Match;events:Event[];layer?:string;playerId?:string;onEvent?:(e:Event)=>void}) {
 const uid=useId().replace(/:/g,'');
 const filtered=events.filter(e=> (!playerId||e.player_id===playerId) && (layer==='all'||(layer==='shots'?e.event_type==='shot':e.event_type==='recovery')));
 const visible=filtered.slice(layer==='all'?-16:-40);
 const point=(e:Event,end=false)=>e.team_id===match.home.id?[end?e.end_x:e.start_x,end?e.end_y:e.start_y]:[105-(end?e.end_x:e.start_x),68-(end?e.end_y:e.start_y)];
 const color=(e:Event)=>e.team_id===match.home.id?match.home.color:match.away.color;
 return <svg className="pitch" viewBox="-4 -4 113 76" role="img" aria-label={`${layer==='shots'?'Shot map':'Event location map'} for ${match.title}. Dots are observed events, not player tracking.`}>
 <defs><pattern id={uid} width="13.125" height="68" patternUnits="userSpaceOnUse"><rect width="6.5625" height="68" fill="#ffffff" opacity=".018"/></pattern><radialGradient id={`${uid}-g`}><stop stopColor="#a7ef64" stopOpacity=".4"/><stop offset="1" stopColor="#a7ef64" stopOpacity="0"/></radialGradient></defs>
 <rect x="-4" y="-4" width="113" height="76" rx="2" fill="#10231d"/><rect width="105" height="68" fill={`url(#${uid})`}/>
 <g fill="none" stroke="#658379" strokeWidth=".32" opacity=".7"><rect width="105" height="68"/><path d="M52.5 0V68"/><circle cx="52.5" cy="34" r="9.15"/><circle cx="52.5" cy="34" r=".5" fill="#658379"/><path d="M0 13.84H16.5V54.16H0M105 13.84H88.5V54.16H105M0 24.84H5.5V43.16H0M105 24.84H99.5V43.16H105M0 30.34H-1.5V37.66H0M105 30.34H106.5V37.66H105"/><circle cx="11" cy="34" r=".4"/><circle cx="94" cy="34" r=".4"/><path d="M16.5 26.7A9.15 9.15 0 0 1 16.5 41.3M88.5 26.7A9.15 9.15 0 0 0 88.5 41.3"/></g>
 <path d="M70 0V68M35 0V68" stroke="#a7ef64" strokeDasharray="1 2" opacity=".12" strokeWidth=".3"/>
 {visible.map((e,i)=>{const [x,y]=point(e);const [ex,ey]=point(e,true);return <g key={e.event_id} onClick={()=>onEvent?.(e)} className={onEvent?'map-event':''} opacity={.35+.65*(i+1)/visible.length}>
 {['pass','carry','shot'].includes(e.event_type)&&<path d={`M${x} ${y}L${ex} ${ey}`} stroke={color(e)} strokeWidth={e.event_type==='shot'?'.65':'.35'} strokeDasharray={e.event_type==='carry'?'1 1':undefined}/>}
 <circle cx={x} cy={y} r={e.event_type==='shot'?1.5:1.15} fill={color(e)} stroke="#0e1718" strokeWidth=".4"/><title>{e.event_type} · {e.player_id} · {Math.floor(e.match_clock_ms/60000)}′ · {e.outcome}</title></g>})}
 {layer==='all'&&visible.length>0&&(()=>{const [x,y]=point(visible[visible.length-1],true);return <><circle cx={x} cy={y} r="7" fill={`url(#${uid}-g)`}/><circle cx={x} cy={y} r="1" fill="#fff" stroke="#a7ef64" strokeWidth=".4"/></>})()}
 <text x="2" y="72" fill="#8fa49a" fontSize="1.8" letterSpacing=".35">HARBOR CITY →</text><text x="103" y="72" textAnchor="end" fill="#8fa49a" fontSize="1.8" letterSpacing=".35">← VALE ATHLETIC</text>
 </svg>
}
