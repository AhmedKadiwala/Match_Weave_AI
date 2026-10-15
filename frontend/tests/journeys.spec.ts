import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';

test.beforeEach(async({page})=>{await page.goto('/');await expect(page.getByRole('heading',{name:'The match, beyond the score.'})).toBeVisible()});

test('replay, temporal consistency, personas, multilingual story and evidence',async({page})=>{
 const narrative=page.locator('.story-text');const analyst=await narrative.textContent();
 await page.getByRole('button',{name:'Casual fan',exact:true}).click();await expect(narrative).not.toHaveText(analyst!);
 await page.getByLabel('Narrative language').selectOption('hi');await expect(narrative).toContainText('पिछले');
 await page.getByLabel('Narrative language').selectOption('es');await expect(narrative).toContainText('últimos');
 await page.getByLabel('Narrative language').selectOption('en');
 await page.getByRole('button',{name:'Explore evidence'}).click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('.evidence-event').first()).toBeVisible();
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByLabel('Restart replay').click();await expect(page.locator('.match-clock')).toContainText('00:00');await expect(page.getByText('Play five minutes')).toBeVisible();
 await page.getByLabel('Play replay').click();await expect(page.getByLabel('Pause replay')).toBeVisible();await expect(page.locator('.match-clock')).not.toContainText('00:00');await page.getByLabel('Pause replay').click();
});

test('all scenarios and full time recaps have their authored scorelines',async({page})=>{
 for(const [id,score] of [['comeback','3:2'],['pressing','2:1'],['counter','2:1'],['defensive','0:1'],['star','3:1']]){
  await page.getByLabel('Match scenario').selectOption(id);await expect(page.locator('.score-main')).toBeVisible();
  await page.getByRole('button',{name:'Match recap',exact:true}).click();
  await expect(page.locator('.score>div')).toHaveText(score);
  await expect(page.locator('.recap-hero')).toContainText('FULL-TIME');
 }
});

test('player focus, filtering and all six views render actual data',async({page})=>{
 await page.getByRole('button',{name:'Analyst control room',exact:true}).click();await expect(page.getByRole('heading',{name:'Player comparison'})).toBeVisible();
 await page.getByLabel('Pitch layer').selectOption('shots');await expect(page.getByRole('img',{name:/Shot map/})).toBeVisible();
 await page.getByLabel('Event filter').selectOption('shot');await expect(page.locator('.event-list')).toContainText('shot');
 await page.getByRole('button',{name:'Your match',exact:true}).click();await page.getByLabel('Favorite club').selectOption('vale');
 await expect(page.locator('.story-text')).toContainText('Vale');await page.getByLabel('Favorite player').selectOption('vale-9');await expect(page.locator('.player-profile')).toContainText('Remy Cole');
 await page.getByRole('button',{name:'Agent intelligence',exact:true}).click();await expect(page.locator('.trace-card')).toHaveCount(5);
 await page.getByRole('button',{name:'Inspect failure recovery',exact:true}).click();await expect(page.locator('.trace-card.rejected')).toHaveCount(1);await expect(page.locator('.trace-card')).toHaveCount(7);
 await page.locator('.trace-card.rejected summary').click();await expect(page.locator('.trace-card.rejected')).toContainText('numerical claim');
});

test('broadcast preview exports evidence-linked timed JSON',async({page})=>{
 await page.getByRole('button',{name:'Broadcast studio',exact:true}).click();await page.getByLabel('Overlay format').selectOption('stat_card');
 await expect(page.locator('.broadcast-graphic')).toHaveClass(/stat_card/);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export overlay JSON'}).click();const file=await download;expect(file.suggestedFilename()).toContain('overlay.json');
 const stream=await file.createReadStream();let text='';for await(const chunk of stream!)text+=chunk;const payload=JSON.parse(text);expect(payload.verification_status).toBe('verified');expect(payload.source_event_ids.length).toBeGreaterThan(0);expect(payload.end_ms).toBeGreaterThan(payload.start_ms);expect(payload.overlay_type).toBe('stat_card');
 await page.getByRole('button',{name:'Hide graphic',exact:true}).click();await expect(page.locator('.broadcast-graphic')).toHaveCount(0);
});

test('frontend connects to real Python backend and executes a verified workflow',async({page})=>{
 await page.getByRole('button',{name:'Connect local backend',exact:true}).click();await expect(page.getByRole('button',{name:'Local backend connected'})).toBeVisible();
 await page.getByRole('button',{name:'Agent intelligence',exact:true}).click();await page.getByRole('button',{name:'Run workflow',exact:true}).click();await expect(page.getByText('Fresh local workflow',{exact:true})).toBeVisible();await expect(page.locator('.trace-card')).toHaveCount(5);
});

test('responsive layout, keyboard dialog and genuine screenshots',async({page})=>{
 await mkdir('../docs/screenshots',{recursive:true});
 await page.screenshot({path:'../docs/screenshots/01-live-intelligence.png',fullPage:true});
 for(const [button,name] of [['Analyst control room','02-analyst'],['Your match','03-personalized'],['Broadcast studio','04-broadcast'],['Agent intelligence','05-agents'],['Match recap','06-recap']]){await page.getByRole('button',{name:button,exact:true}).click();await page.screenshot({path:`../docs/screenshots/${name}.png`,fullPage:true})}
 await page.getByRole('button',{name:'Live intelligence',exact:true}).click();
 for(const width of [1024,768,390]){await page.setViewportSize({width,height:1000});await expect(page.locator('.scoreboard')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();await page.screenshot({path:`../docs/screenshots/responsive-${width}.png`,fullPage:true})}
 await page.getByRole('button',{name:'Explore evidence'}).click();await page.keyboard.press('Tab');await expect(page.getByLabel('Close evidence inspector')).toBeFocused();await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('static demo works with no network except its own artifact host',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:5173')?r.continue():r.abort());
 await page.reload();await expect(page.getByRole('heading',{name:'The match, beyond the score.'})).toBeVisible();
 await page.getByLabel('Narrative language').selectOption('es');await expect(page.locator('.story-text')).toContainText('últimos');expect(errors).toEqual([]);
});
