'use client';
import React, { useEffect, useState, useRef } from 'react';
import { settingsAPI } from '../../../../api/settings/api';
import styles from '../settings.module.scss';

interface NotificationSettings {
  email_notifications: boolean;
  project_notifications: boolean;
  like_comment_notifications: boolean;
  template_notifications: boolean;
  weekly_newsletter: boolean;
}

export default function NotificationSettings() {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const didFetch = useRef(false);

  useEffect(() => {
    if (didFetch.current) return;
    didFetch.current = true;
    async function fetchSettings() {
      setLoading(true);
      try {
        const data = await settingsAPI.getNotificationSettings();
        setSettings(data.notification_settings);
      } catch (e) {
        setError('Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    }
    fetchSettings();
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!settings) return;
    setSettings({ ...settings, [e.target.name]: e.target.checked });
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await settingsAPI.updateNotificationSettings(settings);
      setSaving(false);
    } catch (e) {
      setError('Ошибка сохранения');
      setSaving(false);
    }
  }

  if (loading) return <div className={styles.textGray}>Загрузка...</div>;
  if (error) return <div className={styles.textRed}>{error}</div>;
  if (!settings) return null;

  return (
    <form className={styles.section} onSubmit={handleSave}>
      <h2 className={styles.sectionTitle}>Уведомления</h2>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="email_notifications"
            checked={settings.email_notifications}
            onChange={handleChange}
          />
          Email-уведомления
        </label>
      </div>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="project_notifications"
            checked={settings.project_notifications}
            onChange={handleChange}
          />
          О новых проектах
        </label>
      </div>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="like_comment_notifications"
            checked={settings.like_comment_notifications}
            onChange={handleChange}
          />
          О лайках и комментариях
        </label>
      </div>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="template_notifications"
            checked={settings.template_notifications}
            onChange={handleChange}
          />
          О новых шаблонах
        </label>
      </div>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="weekly_newsletter"
            checked={settings.weekly_newsletter}
            onChange={handleChange}
          />
          Еженедельная рассылка
        </label>
      </div>
      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>
    </form>
  );
} 