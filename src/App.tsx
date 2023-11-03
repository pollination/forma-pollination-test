import React, { ChangeEvent, useState } from 'react'
import './App.css'
import { MyComponent } from './MyComponent'

function App() {
  const [apiKey, setApiKey] = useState<string>('')

  function handleOnChange(event: ChangeEvent<HTMLInputElement>): void {
    setApiKey(event.target.value)
  }

  return (
    <div className='App'>
    <div>
      <label htmlFor='apikey'>Pollination API Key:</label>
      <input type='password' id='apikey' name='apikey' onChange={handleOnChange}/>
    </div>
      <MyComponent password={apiKey}/>
    </div>
  )
}

export default App
