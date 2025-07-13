'use client';
import React, { useEffect, useState, useRef } from 'react';
import { settingsAPI } from '../../../../api/settings/api';
import styles from '../settings.module.scss';

// Пример структуры профиля
interface Profile {
  avatar_url?: string;
  bio: string | null;
  location: string | null;
  birth_date: string | null;
  gender: string | null;
  social_links: {
    github?: string | null;
    linkedin?: string | null;
    twitter?: string | null;
    instagram?: string | null;
    website?: string | null;
  };
  profile_visibility: string;
  // ... другие поля
}

const GENDER_OPTIONS = [
  { value: '', label: 'Не выбрано' },
  { value: 'male', label: 'Мужской' },
  { value: 'female', label: 'Женский' },
  { value: 'other', label: 'Другое' },
  { value: 'prefer_not_to_say', label: 'Не указывать' },
];

export default function ProfileSettings() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const didFetch = useRef(false);

  // Получение профиля
  useEffect(() => {
    if (didFetch.current) return;
    didFetch.current = true;
    async function fetchProfile() {
      setLoading(true);
      try {
        const data = await settingsAPI.getProfile();
        setProfile(data.profile);
      } catch (e) {
        setError('Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  // Обработка изменения полей
  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    if (!profile) return;
    setProfile({ ...profile, [e.target.name]: e.target.value });
  }

  // Сохранение профиля
  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await settingsAPI.updateProfile(profile);
      setSaving(false);
    } catch (e) {
      setError('Ошибка сохранения');
      setSaving(false);
    }
  }

  if (loading) return <div className={styles.textGray}>Загрузка...</div>;
  if (error) return <div className={styles.textRed}>{error}</div>;
  if (!profile) return null;

  return (
    <form className={styles.section} onSubmit={handleSave}>
      <h2 className={styles.sectionTitle}>Профиль</h2>
      <div className={styles.formRow}>
        <label>Биография</label>
        <textarea
          name="bio"
          value={profile.bio || ""}
          onChange={handleChange}
          className={styles.input}
          rows={3}
        />
      </div>
      <div className={styles.formRow}>
        <label>Локация</label>
        <input
          name="location"
          value={profile.location || ""}
          onChange={handleChange}
          className={styles.input}
        />
      </div>
      <div className={styles.formRow}>
        <label>Дата рождения</label>
        <input
          type="date"
          name="birth_date"
          value={profile.birth_date || ""}
          onChange={handleChange}
          className={styles.input}
        />
      </div>
      <div className={styles.formRow}>
        <label>Пол</label>
        <select
          name="gender"
          value={profile.gender || ""}
          onChange={handleChange}
          className={styles.input}
        >
          {GENDER_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      <div className={styles.formRow}>
        <label>GitHub</label>
        <input
          name="social_links.github"
          value={profile.social_links.github || ""}
          onChange={e => setProfile({ ...profile, social_links: { ...profile.social_links, github: e.target.value || "" } })}
          className={styles.input}
        />
      </div>
      {/* Можно добавить другие соцсети аналогично */}
      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>
    </form>
  );
} 