import React from 'react';
import './Post.css';

const Post = ({username, userImage, postImage, likes, caption }) => {
    return(
        <div className='post-container'>
            {/*cabecera del post */}
            <div className='post-header'>
                <img className='post-avatar' src={userImage} alt={username}/>
                <span className='post-username'>{username}</span>
            </div>

            {/*Imagen principal */}
            <img className='post-image' src={postImage} alt="Contenido del post" />

            {/*Seccion de interaccion */}
            <div className="post-content">
                <div className="post-icons">
                    <span className="icon">❤️</span>
                    <span className="icon">💬</span>
                    <span className="icon">✈️</span>
                </div>

                <p className="post-likes"><strong>{likes} Me gusta</strong></p>
                
                <p className="post-description">
                    <strong>{username}</strong>{caption}
                </p>
            </div>
        </div>
    );
};

export default Post;