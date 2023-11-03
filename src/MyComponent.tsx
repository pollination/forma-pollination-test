import { Configuration } from '@pollination-solutions/pollination-sdk'
import { useAPIClient, AuthUser, SelectRecipe, SelectProject, SelectAccount } from 'pollination-react-io'
import { Account } from 'pollination-react-io/build/SelectAccount/SelectAccount.types'
import React, { useEffect, useMemo, useState } from 'react'
import { Forma } from 'forma-embedded-view-sdk/auto'

interface MyComponentProps {
  password: string
}

export const MyComponent: React.FC<MyComponentProps> = ({
  password
}) => {
  const [buildingPaths, setBuildingPaths] = useState<string[]>()
  const [accountInfo, setAccountInfo] = useState<string>()

  const config = useMemo(() => ({ 
    apiKey: password,
  } as Configuration), [password])
  
  const { authUser, client } = useAPIClient(config)

  function handleOnChange(account: Account): void {
    if (!account) return
    
    setAccountInfo(JSON.stringify(account, null, 2))
  }

  useEffect(() => {
    const fetchData = async () => {
      Forma.geometry
        .getPathsByCategory({ category: "building" })
        .then(setBuildingPaths)
    }
    fetchData()
  }, [])

  return (
    <div className="App">
      <div>
        <h3>Use FormAPI</h3>
        <p>Total number of buildings: {buildingPaths?.length}</p>
      </div>
      <div>
        <h3>Use Pollination</h3>
        <AuthUser { ...config } />
        <h5>Account</h5>
        <SelectAccount 
          client={client.current} 
          authUser={authUser} 
          onChange={handleOnChange} />
        <div><pre>{accountInfo}</pre></div>
      </div>
    </div>
  )
}