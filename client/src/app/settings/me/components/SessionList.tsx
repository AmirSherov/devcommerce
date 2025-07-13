'use client';
import React, { useEffect, useState } from 'react';
import { settingsAPI } from '../../../../api/settings/api';
import styles from '../settings.module.scss';

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  last_activity: string;
  is_active: boolean;
  device_info: string;
  browser_info: string;
  is_expired: boolean;
  is_current_session: boolean;
  days_since_first_login: number;
  can_manage_sessions: boolean;
  session_trusted: boolean;
}

export default function SessionList() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [canManage, setCanManage] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSessions() {
      setLoading(true);
      try {
        const data = await settingsAPI.getSessions();
        setSessions(data.sessions);
        setCanManage(data.can_manage_sessions);
        setInfo(`Управлять сессиями можно только с доверенного устройства (3+ дня).`);
      } catch (e) {
        setError('Ошибка загрузки сессий');
      } finally {
        setLoading(false);
      }
    }
    fetchSessions();
  }, []);

  async function terminateSession(id: string) {
    if (!canManage) return;
    if (!window.confirm('Завершить эту сессию?')) return;
    try {
      await settingsAPI.terminateSession(id);
      setSessions(sessions => sessions.filter(s => s.id !== id));
    } catch {
      setError('Ошибка завершения сессии');
    }
  }

  async function terminateAll() {
    if (!canManage) return;
    if (!window.confirm('Завершить все сессии кроме текущей?')) return;
    try {
      await settingsAPI.terminateAllSessions();
      setSessions(sessions => sessions.filter(s => s.is_current_session));
    } catch {
      setError('Ошибка завершения сессий');
    }
  }

  if (loading) return <div className={styles.textGray}>Загрузка сессий...</div>;
  if (error) return <div className={styles.textRed}>{error}</div>;

  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>Активные сессии</h3>
      {info && <div className={styles.textGray}>{info}</div>}
      <table className={styles.sessionTable}>
        <thead>
          <tr>
            <th>IP</th>
            <th>Устройство</th>
            <th>Браузер</th>
            <th>Последняя активность</th>
            <th>Статус</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {sessions.map(s => (
            <tr key={s.id} className={s.is_current_session ? styles.currentSession : ''}>
              <td>{s.ip_address}</td>
              <td>{s.device_info}</td>
              <td>{s.browser_info}</td>
              <td>{new Date(s.last_activity).toLocaleString()}</td>
              <td>{s.is_current_session ? 'Текущая' : (s.is_active ? 'Активна' : 'Завершена')}</td>
              <td>
                {!s.is_current_session && canManage && s.is_active && (
                  <button className={styles.terminateBtn} onClick={() => terminateSession(s.id)}>
                    Завершить
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {canManage && (
        <button className={styles.terminateAllBtn} onClick={terminateAll}>
          Завершить все кроме текущей
        </button>
      )}
    </div>
  );
} 