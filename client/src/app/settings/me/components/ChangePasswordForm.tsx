'use client';
import React, { useState } from 'react';
import { settingsAPI } from '../../../../api/settings/api';
import styles from '../settings.module.scss';

export default function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await settingsAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (e) {
      setError('Ошибка смены пароля');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className={styles.formRow} onSubmit={handleSubmit} style={{ marginBottom: 32 }}>
      <label>Смена пароля</label>
      <input
        type="password"
        placeholder="Текущий пароль"
        value={currentPassword}
        onChange={e => setCurrentPassword(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="password"
        placeholder="Новый пароль"
        value={newPassword}
        onChange={e => setNewPassword(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="password"
        placeholder="Повторите новый пароль"
        value={confirmPassword}
        onChange={e => setConfirmPassword(e.target.value)}
        className={styles.input}
        required
      />
      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сменить пароль'}
      </button>
      {error && <div className={styles.textRed}>{error}</div>}
      {success && <div className={styles.textGreen}>Пароль успешно изменён</div>}
    </form>
  );
} 