import { useState } from 'react'
import './css/Sidebar.css'
export default function SideBar({onNewChat,currentUser,onLogout}){
    const [showMenu,setshowMenu]=useState(false)
    const onMenuClick=()=>{
        setshowMenu(prev => !prev);
    }
    return (
    <div className='sidebar-container'>
        <div className='sidebar-header'>BookBot</div>
        <button className='sidebar-button' onClick={()=>onNewChat()}>+ New Chat</button>
        <div className='user-menu'>
            <div className='sidebar-current-user' onClick={onMenuClick}>{currentUser}{showMenu ? '▲' : '▼'}</div>
            {showMenu && (<div className='user-dropdown'><button onClick={onLogout}>Log Out</button></div>)}    
        </div>    
    </div>
)
}