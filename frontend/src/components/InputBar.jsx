import { useState,useRef,useEffect } from "react"
import './css/InputBar.css'
import Papa from 'papaparse'
export default function InputBar({onSend,onFileUpload}){
    const [inputText,setInputText]=useState('');
    const textareaRef=useRef(null);
    const [fileName,setFileName]=useState('');
    const fileInputRef=useRef(null);

    const handleFileUpload=((e)=>{
        if (e.target.files && e.target.files[0]){
            setFileName(e.target.files[0].name);
            Papa.parse(e.target.files[0],{header:true,complete:(results)=>{
                const filtered = results.data.map(row => ({
                    title: row['Title'],
                    author: row['Author'],
                    rating: row['My Rating'],
                    shelf: row['Exclusive Shelf'],
                    dateRead: row['Date Read']
                }))
                onFileUpload(filtered)
            }})
        }
    })
    const handleClick=()=>{
        if (inputText.trim()){
            onSend(inputText)
            setInputText('')
            setFileName('')
        }
    }
    useEffect(()=>{
       const textarea=textareaRef.current
       if (textarea){
        textarea.style.height='auto';
        textarea.style.height=`${Math.min(textarea.scrollHeight, 200)}px`;
       }
       if (textarea.scrollHeight<200){
        textarea.style.overflowY='hidden';
       }
       else{
        textarea.style.overflowY='auto'
       }
    },[inputText]);
    return(
        <div className="input-bar-wrapper">
            {fileName && <div className="file-indicator">{fileName} ✓</div>}
            <div className="input-bar-container">
            <button type="button" className="attach-button" onClick={()=>fileInputRef.current.click()}>+</button>
            <input type="file" accept=".csv" ref={fileInputRef} onChange={handleFileUpload} style={{display:'none'}}/>
            <label className="label-container">
                <textarea className="input-area" onKeyDown={(e)=>{if (e.key==="Enter" && !e.shiftKey){handleClick(); e.preventDefault()}}} ref={textareaRef} value={inputText} style={{resize:'none'}} onChange={(e)=>setInputText(e.target.value)} rows={1} name="input-area" placeholder={"Write a message..."}/>
            </label>
            <button className="input-button" onClick={handleClick} disabled={!inputText.trim()}><span>&uarr;</span></button>
            </div>
        </div>
    )   
}