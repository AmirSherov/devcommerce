'use client';
import React from 'react';
import styles from '../settings.module.scss';
import ChangePasswordForm from './ChangePasswordForm';
import SessionList from './SessionList';

export default function SecuritySettings() {
  return (
    <div className={styles.section}>
      <h2 className={styles.sectionTitle}>Безопасность</h2>
      <ChangePasswordForm />
      <SessionList />
    </div>
  );
} 