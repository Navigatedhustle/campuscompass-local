/// <reference types="vite/client" />
import {useEffect,useRef,useState} from 'react';
import {getDocument,GlobalWorkerOptions} from 'pdfjs-dist';
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
GlobalWorkerOptions.workerSrc=workerUrl;
export function PdfViewer({url}:{url:string}){
 const container=useRef<HTMLDivElement>(null),[error,setError]=useState(''),[pages,setPages]=useState(0),[ready,setReady]=useState(false);
 useEffect(()=>{
  let cancelled=false;setError('');setPages(0);setReady(false);container.current?.replaceChildren();
  const task=getDocument({url,withCredentials:true,isEvalSupported:false,useSystemFonts:false});
  task.promise.then(async pdf=>{
   if(cancelled)return;setPages(pdf.numPages);
   for(let n=1;n<=pdf.numPages;n++){
    const page=await pdf.getPage(n);if(cancelled)return;
    const viewport=page.getViewport({scale:1.5});const canvas=document.createElement('canvas');canvas.className='pdf-page';canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);canvas.setAttribute('aria-label',`PDF page ${n} of ${pdf.numPages}`);
    await page.render({canvas,canvasContext:canvas.getContext('2d')!,viewport}).promise;
    if(cancelled)return;container.current?.append(canvas);
   }
   if(!cancelled)setReady(true);
  }).catch(()=>{if(!cancelled)setError('The local PDF could not be displayed. Use Download PDF or open the source document.');});
  return()=>{cancelled=true;void task.destroy();};
 },[url]);
 return <div className="pdf-viewer" data-ready={ready?'true':'false'}><p className="pdf-viewer-status" aria-live="polite">{error||(!ready?'Rendering the local PDF…':`${pages} pages · Rendered locally`)}</p><div ref={container}/></div>;
}
