import './css/MessageBubbles.css'
import { useState } from 'react';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Copy, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
export default function MessageBubbles({message}){
    const isOwnMessage=message.role=== 'user'
    const [copyText,setCopyText]=useState(false);
    return(
        <div className={`message ${isOwnMessage ? 'ownmessage': 'botmessage'}`}>
            <div className="message-bubble">
                {!isOwnMessage && <div className="message-user">{message.role}</div>}
                <div className="message-content">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
                <div className="message-time">{new Date(message.timestamp).toLocaleTimeString('en-US', {hour: '2-digit',minute: '2-digit'})}</div>
            </div>
            <CopyToClipboard text={message.content} onCopy={()=>{setCopyText(true); setTimeout(()=>setCopyText(false),2000)}}>
                <button className='copy-button'>{copyText ? <Check size={14}/> : <Copy size={14}/>}</button>
            </CopyToClipboard>
        </div>
    );
}