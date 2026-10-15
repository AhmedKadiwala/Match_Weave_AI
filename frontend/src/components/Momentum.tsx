import type {State,Match} from '../types';
export function Momentum({state,match,onSeek}:{state:State;match:Match;onSeek:(ms:number)=>void}){
 const max=Math.max(1,...state.momentum.flatMap(b=>[b[match.home.id],b[match.away.id]]));
 return <div className="momentum"><div className="momentum-chart" aria-label="Attacking momentum, five-minute weighted event proxy">
 {Array.from({length:18},(_,i)=>{const b=state.momentum.find(v=>v.minute===(i+1)*5);return <button key={i} title={`${(i+1)*5} minutes: ${b?`${match.home.short} ${b[match.home.id]}, ${match.away.short} ${b[match.away.id]}`:'not played yet'}`} aria-label={`Seek to ${(i+1)*5} minutes`} onClick={()=>onSeek((i+1)*300000)} className="momentum-bin"><span className="home-bar" style={{height:`${b?b[match.home.id]/max*44:0}%`}}/><span className="away-bar" style={{height:`${b?b[match.away.id]/max*44:0}%`}}/></button>})}
 <div className="midline"/></div><div className="axis"><span>00′</span><span>15′</span><span>30′</span><span>HT</span><span>60′</span><span>75′</span><span>90′</span></div></div>
}
