'use client';
import React, { useEffect, useState, useRef } from 'react';
import { settingsAPI } from '../../../../api/settings/api';
import styles from '../settings.module.scss';

interface Privacy {
  profile_visibility: string;
  projects_visibility: string;
  portfolio_visibility: string;
  notify_new_followers: boolean;
}

const VISIBILITY_OPTIONS = [
  { value: 'public', label: 'Публично' },
  { value: 'private', label: 'Только я' },
];

export default function PrivacySettings() {
  const [privacy, setPrivacy] = useState<Privacy | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const didFetch = useRef(false);

  useEffect(() => {
    if (didFetch.current) return;
    didFetch.current = true;
    async function fetchPrivacy() {
      setLoading(true);
      try {
        const data = await settingsAPI.getProfile();
        setPrivacy({
          profile_visibility: data.profile.profile_visibility,
          projects_visibility: data.profile.projects_visibility,
          portfolio_visibility: data.profile.portfolio_visibility,
          notify_new_followers: data.profile.notify_new_followers,
        });
      } catch (e) {
        setError('Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    }
    fetchPrivacy();
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    if (!privacy) return;
    const { name, value, type, checked } = e.target;
    setPrivacy({ ...privacy, [name]: type === 'checkbox' ? checked : value });
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await settingsAPI.updateProfile(privacy);
      setSaving(false);
    } catch (e) {
      setError('Ошибка сохранения');
      setSaving(false);
    }
  }

  if (loading) return <div className={styles.textGray}>Загрузка...</div>;
  if (error) return <div className={styles.textRed}>{error}</div>;
  if (!privacy) return null;

  return (
    <form className={styles.section} onSubmit={handleSave}>
      <h2 className={styles.sectionTitle}>Приватность</h2>
      <div className={styles.formRow}>
        <label>Видимость профиля</label>
        <select
          name="profile_visibility"
          value={privacy.profile_visibility}
          onChange={handleChange}
          className={styles.input}
        >
          {VISIBILITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      <div className={styles.formRow}>
        <label>Видимость проектов</label>
        <select
          name="projects_visibility"
          value={privacy.projects_visibility}
          onChange={handleChange}
          className={styles.input}
        >
          {VISIBILITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      <div className={styles.formRow}>
        <label>Видимость портфолио</label>
        <select
          name="portfolio_visibility"
          value={privacy.portfolio_visibility}
          onChange={handleChange}
          className={styles.input}
        >
          {VISIBILITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      <div className={styles.formRow}>
        <label>
          <input
            type="checkbox"
            name="notify_new_followers"
            checked={privacy.notify_new_followers}
            onChange={handleChange}
          />
          Уведомлять о новых подписчиках
        </label>
      </div>
      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>
    </form>
  );
} 