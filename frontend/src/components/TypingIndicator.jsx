import './css/TypingIndicator.css'


export default function TypingIndicator(){
    return(
        <div className='typing-indicator'>
            <div className="flex items-center space-x-2 bg-gray-100 p-4 rounded-2xl w-max" style={{backgroundColor:"#2a2a2a"}}>
                <span className="text-sm font-medium text-gray-400 mr-1">AI is thinking</span>
                {[0, 1, 2].map((index) => (
            <div key={index} className="w-2.5 h-2.5 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: `${index * 0.15}s`,animationDuration: '1s'}}/>
      ))}
        </div>
        </div>
    )
}