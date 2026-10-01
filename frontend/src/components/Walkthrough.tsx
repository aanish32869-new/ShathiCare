import {useEffect, useState} from 'react';
import {ArrowLeft, ArrowRight, MousePointer2, X} from 'lucide-react';

type AppScreen='home'|'flow'|'result'|'docs'|'confirm'|'done'|'chat';
type Props={lang:'en'|'ta';screen:AppScreen;onGuideNavigate?:(screen:AppScreen)=>void};
type Slide={screen:AppScreen;target:string;title:string;body:string;permission?:boolean};

// Each stop names a real, visible control. The first six preserve the short
// guided journey; the remaining stops cover the rest of the site's controls.
const slides:Slide[]=[
 {screen:'home',target:'.heroCopy > .primary',title:'Tap the green button to begin',body:'This starts the guided PMMVY questions. You can also use the voice button below it.'},
 {screen:'flow',target:'.answers',title:'Tap Yes or No for each question',body:'Choose the answer that fits you. One simple question appears at a time.'},
 {screen:'flow',target:'.voiceButton',title:'Tap the microphone to speak',body:'Say your answer in the language you know. Your browser may ask for microphone permission.'},
 {screen:'flow',target:'.voiceButton',title:'When asked, tap Allow for the microphone',body:'Tap Allow in the browser permission box near the address bar. Touch answers still work if you choose Block.',permission:true},
 {screen:'flow',target:'.gestureRow',title:'You can use hand signs too',body:'These buttons let you go back, answer Yes or No, move to the next question, or get help.'},
 {screen:'flow',target:'.helpLink',title:'Tap Help whenever you need it',body:'Help explains the current step and lets you replay this visual guide.'},

 {screen:'home',target:'.language',title:'Choose your language',body:'Use this menu to switch between the available interface languages.'},
 {screen:'home',target:'.demoToggle',title:'Turn demo mode on or off',body:'Demo mode uses sample answers so you can explore without sending an eligibility request.'},
 {screen:'home',target:'.voiceAssistantButton',title:'Speak in your language',body:'Tap here to use voice input. Your browser will ask before enabling the microphone.'},
 {screen:'home',target:'.guideTrigger',title:'Replay the visual guide',body:'Open this guide again whenever you want a reminder.'},
 {screen:'home',target:'.brand',title:'Return to the welcome screen',body:'The SakhiCare name at the top takes you back to the start.'},

 {screen:'flow',target:'.chatNav',title:'Open Talk with Sakhi',body:'This opens the separate chat screen for questions, voice conversation, and file uploads.'},
 {screen:'flow',target:'.progressTop .iconButton',title:'Go back one step',body:'Use this arrow to return to the previous question or to the welcome screen.'},
 {screen:'flow',target:'.helpLink',title:'Open step-by-step help',body:'This explains the question and shows the visual guide again.'},
 {screen:'flow',target:'.answer.yes',title:'Choose Yes',body:'Tap Yes when this answer is true for you.'},
 {screen:'flow',target:'.answer.no',title:'Choose No',body:'Tap No when this answer is not true for you.'},
 {screen:'flow',target:'.voiceButton',title:'Answer with your voice',body:'Start speaking after tapping the microphone. You can answer by touch if voice is unavailable.'},
 {screen:'flow',target:'.cameraStrip button',title:'Turn on gesture detection',body:'Camera access is optional. The touch buttons remain available if you keep it off.'},
 {screen:'flow',target:'.gestureRow button:nth-of-type(1)',title:'Use the Back hand button',body:'This returns to the previous question.'},
 {screen:'flow',target:'.gestureRow button:nth-of-type(2)',title:'Use the Yes hand button',body:'This records a Yes answer for the current question.'},
 {screen:'flow',target:'.gestureRow button:nth-of-type(3)',title:'Use the No hand button',body:'This records a No answer for the current question.'},
 {screen:'flow',target:'.gestureRow button:nth-of-type(4)',title:'Use the Next hand button',body:'This moves to the next question.'},
 {screen:'flow',target:'.gestureRow button:nth-of-type(5)',title:'Use the Help hand button',body:'This opens an explanation of the current step.'},

 {screen:'result',target:'.resultWrap .primary',title:'Open your checklist',body:'Continue to the document checklist before you visit the official portal.'},
 {screen:'result',target:'.resultWrap .sourceCard a',title:'Read the official scheme information',body:'This link opens the government scheme information in a new tab.'},
 {screen:'docs',target:'.docsWrap .backText',title:'Return to your guidance',body:'Go back to the previous guidance screen.'},
 {screen:'docs',target:'.explainCard button',title:'Listen to an explanation',body:'Tap this speaker to hear a simple explanation of the document card.'},
 {screen:'docs',target:'.docsWrap .sourceCard a',title:'Open the official information source',body:'This link takes you to the government scheme information.'},
 {screen:'docs',target:'.docsWrap > .primary',title:'Continue to the application information',body:'Review the confirmation before opening the official portal.'},
 {screen:'confirm',target:'.confirmWrap .backText',title:'Go back to your checklist',body:'Return to the checklist if you want to review the documents again.'},
 {screen:'confirm',target:'.confirmCard .primary',title:'Continue to the official portal',body:'This opens the government portal in a new tab. SakhiCare does not submit an application.'},
 {screen:'confirm',target:'.confirmCard .secondary',title:'Stay on SakhiCare',body:'Choose this to cancel and return to the checklist.'},
 {screen:'done',target:'.doneWrap .portalLink',title:'Open the government portal',body:'Continue your application on the official PMMVY website.'},
 {screen:'done',target:'.doneWrap .textButton',title:'Start the guidance again',body:'This resets the questions and returns to the welcome screen.'},
 {screen:'done',target:'.doneWrap .sourceCard a',title:'Open the scheme information',body:'Read more from the official government source.'},

 {screen:'chat',target:'.chatBack',title:'Return to SakhiCare',body:'Use this button to close the chat and return to the main guidance.'},
 {screen:'chat',target:'.chatQuickPrompts button:nth-of-type(1)',title:'Try a suggested question',body:'Tap a suggestion to place it in the message box.'},
 {screen:'chat',target:'.chatQuickPrompts button:nth-of-type(2)',title:'Ask about documents',body:'This suggestion asks which documents to prepare.'},
 {screen:'chat',target:'.chatQuickPrompts button:nth-of-type(3)',title:'Ask for simple steps',body:'This suggestion asks Sakhi to explain the scheme simply.'},
 {screen:'chat',target:'.chatComposer input',title:'Type a message',body:'Write a question here in your own words.'},
 {screen:'chat',target:'.attachButton',title:'Attach a document or image',body:'Choose a file to ask Sakhi about it. Only attach files you want to share.'},
 {screen:'chat',target:'.liveButton',title:'Start or end live voice chat',body:'Use this control to speak with Sakhi in real time.'},
 {screen:'chat',target:'.sendButton',title:'Send your message',body:'This sends the text or selected files to Sakhi.'}
];

const screenNames:Record<AppScreen,{en:string;ta:string}>={home:{en:'WELCOME',ta:'வரவேற்பு'},flow:{en:'QUESTIONS',ta:'கேள்விகள்'},result:{en:'GUIDANCE',ta:'வழிகாட்டல்'},docs:{en:'CHECKLIST',ta:'பட்டியல்'},confirm:{en:'CONFIRM',ta:'உறுதிப்படுத்தல்'},done:{en:'COMPLETE',ta:'முடிந்தது'},chat:{en:'CHAT',ta:'உரையாடல்'}};
const firstVisit=()=>{try{return localStorage.getItem('sakhisetu_follow_guide_v2')!=='true'}catch{return false}};

export default function Walkthrough({lang,screen,onGuideNavigate}:Props){
 const [open,setOpen]=useState(firstVisit),[index,setIndex]=useState(0),[rect,setRect]=useState<DOMRect|null>(null);
 const slide=slides[index];
 const finish=()=>{try{localStorage.setItem('sakhisetu_onboarding_completed','true');localStorage.setItem('sakhisetu_follow_guide_v2','true')}catch{/* The guide also works when browser storage is unavailable. */}setOpen(false);onGuideNavigate?.('home')};
 const goTo=(next:number)=>{const safe=Math.max(0,Math.min(slides.length-1,next));setIndex(safe);onGuideNavigate?.(slides[safe].screen)};
 useEffect(()=>{const replay=()=>{setIndex(0);onGuideNavigate?.('home');setOpen(true)};window.addEventListener('open-sakhisetu-guide',replay);return()=>window.removeEventListener('open-sakhisetu-guide',replay)},[onGuideNavigate]);
 useEffect(()=>{
  if(!open)return;
  if(screen!==slide.screen){onGuideNavigate?.(slide.screen);return}
  let frame=0;
  const update=()=>{const target=document.querySelector<HTMLElement>(slide.target);if(!target){setRect(null);return}setRect(target.getBoundingClientRect())};
  const position=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(update)};
  const target=document.querySelector<HTMLElement>(slide.target);target?.scrollIntoView?.({block:'center',behavior:'smooth'});position();
  window.addEventListener('resize',position);window.addEventListener('scroll',position,true);
  const observer=target&&'ResizeObserver'in window?new ResizeObserver(position):null;if(target)observer?.observe(target);
  return()=>{cancelAnimationFrame(frame);window.removeEventListener('resize',position);window.removeEventListener('scroll',position,true);observer?.disconnect()};
 },[open,index,slide.target,slide.screen,screen,onGuideNavigate]);
 useEffect(()=>{
  if(!open)return;
  const advanceFromTarget=(event:MouseEvent)=>{const clicked=event.target;if(!(clicked instanceof Element)||clicked.closest('.followCard'))return;if(!clicked.closest(slide.target))return;event.preventDefault();event.stopImmediatePropagation();if(index===slides.length-1)finish();else goTo(index+1)};
  document.addEventListener('click',advanceFromTarget,true);return()=>document.removeEventListener('click',advanceFromTarget,true);
 },[open,index,slide.target]);
 const t=(en:string,ta:string)=>lang==='en'?en:ta;
 return <>
  <button className="guideTrigger" onClick={()=>{setIndex(0);onGuideNavigate?.('home');setOpen(true)}}><span className="guidePlay">▶</span>{t('Replay guide','வழிகாட்டியை மீண்டும் காட்டு')}<span className="guideHint">{t('full tour','முழு வழிகாட்டி')}</span></button>
  {open&&<div className="followGuide" role="dialog" aria-modal="true" aria-labelledby="followGuideTitle">
   {rect&&<>
    <div className="followShade" style={{left:0,top:0,width:'100vw',height:Math.max(0,rect.top-7)}}/>
    <div className="followShade" style={{left:0,top:rect.bottom+7,width:'100vw',height:Math.max(0,window.innerHeight-rect.bottom-7)}}/>
    <div className="followShade" style={{left:0,top:rect.top-7,width:Math.max(0,rect.left-7),height:rect.height+14}}/>
    <div className="followShade" style={{left:rect.right+7,top:rect.top-7,width:Math.max(0,window.innerWidth-rect.right-7),height:rect.height+14}}/>
    <div className="followSpotlight" style={{left:rect.left-7,top:rect.top-7,width:rect.width+14,height:rect.height+14}}/>
    <div className="followCursor" style={{left:Math.min(window.innerWidth-48,Math.max(8,rect.left+rect.width*.72)),top:Math.min(window.innerHeight-85,Math.max(8,rect.top+rect.height*.68))}} aria-hidden="true"><MousePointer2 size={38}/><i/></div>
   </>}
   <div className={'followCard '+(rect&&rect.top>window.innerHeight*.52?'followCardTop':'')}>
    <div className="followHeader"><span>{t('FOLLOW ME','என்னைப் பின்தொடரவும்')} · {t(screenNames[slide.screen].en,screenNames[slide.screen].ta)} · {index+1}/{slides.length}</span><div className="followProgress"><i style={{width:`${((index+1)/slides.length)*100}%`}}/></div><button onClick={finish} aria-label={t('Skip guide','வழிகாட்டியைத் தவிர்')}><X size={18}/></button></div>
    <div className="followBody"><span className="followHand" aria-hidden="true">👆</span><div><h2 id="followGuideTitle">{t(slide.title,`இங்கே தொடவும்: ${slide.title}`)}</h2><p>{t(slide.body,'சுட்டிக்காட்டி காட்டும் இடத்தைப் பாருங்கள். பொத்தானைத் தொடவும் அல்லது அடுத்து என்பதை அழுத்தி தொடரவும்.')}</p><small className="followNote">{t('Tap the highlighted control or Next to keep going. Actions run after you finish the guide.','வழிகாட்டியைத் தொடரக் காட்டப்பட்ட பொத்தானை அல்லது அடுத்து என்பதைத் தொடவும். வழிகாட்டியை முடித்த பின் செயல்கள் இயங்கும்.')}</small>{slide.permission&&<div className="permissionDemo"><strong>{t('This site wants to use your microphone','இந்தத் தளம் உங்கள் மைக்ரோஃபோனைப் பயன்படுத்த அனுமதி கேட்கிறது')}</strong><span>{t('Allow','அனுமதி')}</span></div>}</div></div>
    <div className="followControls"><button className="guidePrev" onClick={()=>goTo(index-1)} disabled={index===0}><ArrowLeft size={16}/>{t('Back','பின்')}</button><button className="guideNextText" onClick={finish}>{t('Skip guide','வழிகாட்டியைத் தவிர்')}</button><button className="primary guideNext" onClick={()=>index===slides.length-1?finish():goTo(index+1)}>{index===slides.length-1?t('Finish','முடி'):t('Next','அடுத்து')}<ArrowRight size={17}/></button></div>
   </div>
  </div>}
 </>;
}
