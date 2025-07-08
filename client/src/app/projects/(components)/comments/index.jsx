import React, { useEffect, useState } from 'react';
import './style.scss';
import {
  fetchProjectComments,
  createProjectComment,
  likeProjectComment,
  pinProjectComment,
  deleteProjectComment,
  editProjectComment
} from '@/api/projectcomments/api';
import { IoMdHeart } from 'react-icons/io';
import { FaThumbtack } from 'react-icons/fa';

function Comment({ comment, token, onReply, onLike, onPin, onDelete, onEdit, userId, isChild }) {
  const [showReply, setShowReply] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editText, setEditText] = useState(comment.text);

  return (
    <div className={`project-comment${isChild ? ' project-comment-child' : ''}${comment.is_pinned ? ' project-comment-pinned' : ''}`}>
      <div className="project-comment-header">
        <span className="project-comment-author">{comment.author.full_name || comment.author.username}</span>
        <span className="project-comment-date">{new Date(comment.created_at).toLocaleString()}</span>
        {comment.is_pinned && <span className="project-comment-pin"><FaThumbtack /></span>}
      </div>
      {editMode ? (
        <div className="project-comment-edit-block">
          <textarea value={editText} onChange={e => setEditText(e.target.value)} />
          <button onClick={() => { onEdit(comment.id, editText); setEditMode(false); }}>Сохранить</button>
          <button onClick={() => setEditMode(false)}>Отмена</button>
        </div>
      ) : (
        <div className="project-comment-text">{comment.text}</div>
      )}
      <div className="project-comment-actions">
        <button className={`like-btn${comment.is_liked_by_user ? ' liked' : ''}`} onClick={() => onLike(comment.id)}>
          <IoMdHeart /> {comment.likes_count}
        </button>
        {!isChild && <button onClick={() => setShowReply(!showReply)}>Ответить</button>}
        {!isChild && onPin && <button onClick={() => onPin(comment.id)}>{comment.is_pinned ? 'Открепить' : 'Закрепить'}</button>}
        {userId === comment.author.id && onEdit && <button onClick={() => setEditMode(true)}>Редактировать</button>}
        {userId === comment.author.id && onDelete && <button onClick={() => onDelete(comment.id)}>Удалить</button>}
      </div>
      {!isChild && showReply && (
        <div className="project-comment-reply-block">
          <textarea value={replyText} onChange={e => setReplyText(e.target.value)} placeholder="Ваш ответ..." />
          <button onClick={() => { onReply(comment.id, replyText); setReplyText(''); setShowReply(false); }}>Отправить</button>
        </div>
      )}
      {comment.replies && comment.replies.length > 0 && (
        <div className="project-comment-replies">
          {comment.replies.map(reply => (
            <Comment
              key={reply.id}
              comment={reply}
              token={token}
              onReply={onReply}
              onLike={onLike}
              onPin={onPin}
              onDelete={userId === reply.author.id ? onDelete : undefined}
              onEdit={userId === reply.author.id ? onEdit : undefined}
              userId={userId}
              isChild={true}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ProjectComments({ projectId, token, canPin, userId }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');

  async function loadComments() {
    setLoading(true);
    const data = await fetchProjectComments(projectId, token);
    setComments(data);
    setLoading(false);
  }

  useEffect(() => {
    if (projectId && token) loadComments();
    // eslint-disable-next-line
  }, [projectId, token]);

  async function handleCreate(parentId, text) {
    if (!text.trim()) return;
    await createProjectComment(projectId, { text, parent: parentId || null }, token);
    loadComments();
  }
  async function handleLike(commentId) {
    await likeProjectComment(commentId, token);
    loadComments();
  }
  async function handlePin(commentId) {
    await pinProjectComment(commentId, token);
    loadComments();
  }
  async function handleDelete(commentId) {
    await deleteProjectComment(commentId, token);
    loadComments();
  }
  async function handleEdit(commentId, text) {
    await editProjectComment(commentId, { text }, token);
    loadComments();
  }

  return (
    <div className="project-comments-root">
      <h2>Комментарии</h2>
      <div className="project-comments-new">
        <textarea
          value={newComment}
          onChange={e => setNewComment(e.target.value)}
          placeholder="Оставьте комментарий..."
        />
        <button onClick={() => { handleCreate(null, newComment); setNewComment(''); }}>Отправить</button>
      </div>
      {loading ? (
        <div className="project-comments-loading">Загрузка...</div>
      ) : comments.length === 0 ? (
        <div className="project-comments-empty">Комментариев пока нет</div>
      ) : (
        <div className="project-comments-list">
          {comments.map(comment => (
            <Comment
              key={comment.id}
              comment={comment}
              token={token}
              onReply={handleCreate}
              onLike={handleLike}
              onPin={canPin ? handlePin : undefined}
              onDelete={userId === comment.author.id ? handleDelete : undefined}
              onEdit={userId === comment.author.id ? handleEdit : undefined}
              userId={userId}
              isChild={false}
            />
          ))}
        </div>
      )}
    </div>
  );
}
