import { useState } from "react";
import './css/Register.css'

export default function Register({onLogin,onSwitch}){
    const [formData,setformData]=useState({'name':'','email':'','password':''});
    const [errors,setErrors]=useState({});
    const [isLoading,setisLoading]=useState(false);
    const handleChange=(e)=>{
        const {name,value}=e.target;
        setformData((prev)=>({...prev,[name]:value}));
        if (errors[name]){
            setErrors((prev)=>({...prev,[name]:''}));
        }
    };
    const validateForm=()=>{
        const newErrors={};
        if (!formData.email){
            newErrors.email = 'Email is required';
        }
        else if (!/\S+@\S+\.\S+/.test(formData.email)){
            newErrors.email = 'Please enter a valid email';
        }
        if (!formData.password){
            newErrors.password = 'Password is required';
        }
        else if (formData.password.length<6){
            newErrors.password = 'Password must be at least 6 characters';
        }
        if (!formData.name){
            newErrors.name='Name is required';
        }
        setErrors(newErrors)
        return Object.keys(newErrors).length===0;
    };
    const handleSubmit=async(e)=>{
        e.preventDefault();
        if (!validateForm()) return;
        setisLoading(true);
        try{
            console.log('Submitting data to backend:', formData);
            const res=await fetch('http://localhost:8000/auth/register',{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({email:formData.email,password:formData.password,name:formData.name})
            })
            if (res.ok){
                const data=await res.json();
                localStorage.setItem('token', data.token)
                localStorage.setItem('user', JSON.stringify({name: data.name, email: data.email, user_id: data.user_id}))
                onLogin(data)
                alert('Registeration successful!');
            }
            else{
                alert('Registeration Unsuccessful, try again later!')
            }
            
        }
        catch(error){
            setErrors({ form: 'Invalid email or password' });
            alert(error)
        }
        finally{
            setisLoading(false);
        }
    };
    return (
    <div className="register-container">
        <form onSubmit={handleSubmit} className="register-form" noValidate>
            <h2 className="registration-header">Register</h2>
            {errors.form && <div className="error-form">{errors.form}</div>}
            <div className="input-group">
                <label htmlFor="name">Name</label>
                <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} className="input"/>
                {errors.name && <span className="error-span">{errors.name}</span>}
            </div>
            <div className="input-group">
                <label htmlFor="email">Email</label>
                <input type="email" id="email" name="email" value={formData.email}onChange={handleChange} className="input"/>
                {errors.email && <span className='error-span'>{errors.email}</span>}
            </div>
            <div className="input-group">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} className="input"/>
                {errors.password && <span className="error-span">{errors.password}</span>}
            </div>
            <button type="submit" disabled={isLoading} className="submit-button">{isLoading ? 'Registering' : 'Register'}</button>
            <button type="button" onClick={onSwitch} className="switch-button">Already have an account?</button>
        </form>
    </div>
  );
}