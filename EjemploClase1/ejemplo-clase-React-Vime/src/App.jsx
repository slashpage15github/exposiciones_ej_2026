import { useState } from 'react'

import './App.css'
import Post from './Components/Post/Post'
import miImagen from './Components/img/Cancun.jpeg'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <Post
        username={"David Vazquez"}
        userImage={miImagen}
        postImage={miImagen}
        likes={"1240"}
        caption="Disfrutando del sol en la playa"
        />

      </div>

    </>
  )
}

export default App
