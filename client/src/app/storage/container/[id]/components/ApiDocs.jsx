import React, { useState } from 'react';
import './ApiDocs.scss';

const NAV_SECTIONS = [
  { id: 'intro', label: 'Введение' },
  { id: 'auth', label: 'Аутентификация' },
  { id: 'limits', label: 'Лимиты по тарифам' },
  { id: 'endpoints', label: 'Эндпоинты' },
  { id: 'examples', label: 'Примеры кода' },
  { id: 'faq', label: 'FAQ' },
];

const LIMITS = [
  { plan: 'Standard', reqHour: 1000, reqDay: 10000, fileSize: '50MB', filesPerReq: 5, storage: '5GB' },
  { plan: 'Premium', reqHour: 5000, reqDay: 50000, fileSize: '200MB', filesPerReq: 20, storage: '50GB' },
  { plan: 'Pro', reqHour: 10000, reqDay: 100000, fileSize: '1GB', filesPerReq: 100, storage: 'Безлимитно' },
];

const ENDPOINTS = [
  {
    method: 'POST',
    path: '/api/remote/storage/upload/',
    desc: 'Загрузка файла в контейнер',
    auth: 'X-API-KEY',
    params: [
      { name: 'file', type: 'file', required: true, desc: 'Файл для загрузки' },
      { name: 'filename', type: 'string', required: false, desc: 'Кастомное имя файла' },
      { name: 'is_public', type: 'bool', required: false, desc: 'Публичный доступ' },
    ],
    resp: '{ "id": 123, "filename": "file.jpg", ... }',
  },
  {
    method: 'GET',
    path: '/api/remote/storage/files/',
    desc: 'Получение списка файлов',
    auth: 'X-API-KEY',
    params: [
      { name: 'page', type: 'int', required: false, desc: 'Номер страницы' },
      { name: 'page_size', type: 'int', required: false, desc: 'Размер страницы' },
    ],
    resp: '{ "files": [ ... ] }',
  },
  {
    method: 'GET',
    path: '/api/remote/storage/files/{id}/',
    desc: 'Получение информации о файле',
    auth: 'X-API-KEY',
    params: [
      { name: 'id', type: 'int', required: true, desc: 'ID файла' },
    ],
    resp: '{ "id": 123, "filename": "file.jpg", ... }',
  },
  {
    method: 'DELETE',
    path: '/api/remote/storage/files/{id}/',
    desc: 'Удаление файла',
    auth: 'X-API-KEY',
    params: [
      { name: 'id', type: 'int', required: true, desc: 'ID файла' },
    ],
    resp: '{ "success": true }',
  },
  {
    method: 'GET',
    path: '/api/remote/storage/containers/{id}/stats/',
    desc: 'Детальная статистика контейнера',
    auth: 'JWT',
    params: [
      { name: 'id', type: 'int', required: true, desc: 'ID контейнера' },
    ],
    resp: '{ "files_count": 10, ... }',
  },
  {
    method: 'GET',
    path: '/api/storage/containers/{id}/logs/',
    desc: 'Логи операций по контейнеру',
    auth: 'JWT',
    params: [
      { name: 'id', type: 'int', required: true, desc: 'ID контейнера' },
    ],
    resp: '{ "logs": [ ... ] }',
  },
];

const PY_UPLOAD = `import requests

url = 'https://api.devcommerce.com/api/remote/storage/upload/'
headers = {'X-API-KEY': 'ВАШ_API_KEY'}
files = {'file': open('image.jpg', 'rb')}
resp = requests.post(url, headers=headers, files=files)
print(resp.json())`;

const PY_LIST = `import requests

url = 'https://api.devcommerce.com/api/remote/storage/files/'
headers = {'X-API-KEY': 'ВАШ_API_KEY'}
resp = requests.get(url, headers=headers)
print(resp.json())`;

const PY_GET = `import requests
url = 'https://api.devcommerce.com/api/remote/storage/files/{id}/'
headers = {'X-API-KEY': 'ВАШ_API_KEY'}
resp = requests.get(url, headers=headers)
print(resp.json())`;


const JS_UPLOAD = `const formData = new FormData();
formData.append('file', fileInput.files[0]);
fetch('https://api.devcommerce.com/api/remote/storage/upload/', {
  method: 'POST',
  headers: { 'X-API-KEY': 'ВАШ_API_KEY' },
  body: formData
})
.then(r => r.json())
.then(console.log);`;

const JS_LIST = `fetch('https://api.devcommerce.com/api/remote/storage/files/', {
  headers: { 'X-API-KEY': 'ВАШ_API_KEY' }
})
.then(r => r.json())
.then(console.log);`;

const JS_GET = `fetch('https://api.devcommerce.com/api/remote/storage/files/{id}/', {
  headers: { 'X-API-KEY': 'ВАШ_API_KEY' }
})
.then(r => r.json())
.then(console.log);`;

export default function ApiDocs({ apiKey, limits }) {
  const [activeSection, setActiveSection] = useState('intro');

  return (
    <div className="api-docs-root">
      <aside className="api-docs-nav">
        <h2>Документация API</h2>
        <nav>
          {NAV_SECTIONS.map(section => (
            <button
              key={section.id}
              className={activeSection === section.id ? 'active' : ''}
              onClick={() => setActiveSection(section.id)}
            >
              {section.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="api-docs-content">
        {activeSection === 'intro' && (
          <section id="intro">
            <h1>Публичный Storage API</h1>
            <p>Добро пожаловать в документацию публичного API для работы с файлами и контейнерами DevHub Storage. Здесь вы найдете все необходимые сведения для интеграции, лимиты, примеры кода и ответы на частые вопросы.</p>
          </section>
        )}
        {activeSection === 'auth' && (
          <section id="auth">
            <h2>Аутентификация</h2>
            <p>Для доступа к разным возможностям API используются два типа аутентификации:</p>
            <ul>
              <li><b>X-API-KEY</b> — для публичных операций с файлами.</li>
            </ul>
            <pre className="code-block">
{`
// Пример заголовка для публичного API
X-API-KEY: <ваш_API_KEY>`}
            </pre>
          </section>
        )}
        {activeSection === 'limits' && (
          <section id="limits">
            <h2>Лимиты по тарифам</h2>
            <table className="api-limits-table">
              <thead>
                <tr>
                  <th>Тариф</th>
                  <th>Запросов/час</th>
                  <th>Запросов/день</th>
                  <th>Размер файла</th>
                  <th>Файлов за раз</th>
                  <th>Хранилище</th>
                </tr>
              </thead>
              <tbody>
                {LIMITS.map(lim => (
                  <tr key={lim.plan}>
                    <td>{lim.plan}</td>
                    <td>{lim.reqHour}</td>
                    <td>{lim.reqDay}</td>
                    <td>{lim.fileSize}</td>
                    <td>{lim.filesPerReq}</td>
                    <td>{lim.storage}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
        {activeSection === 'endpoints' && (
          <section id="endpoints">
            <h2>Эндпоинты API</h2>
            {ENDPOINTS.map(ep => (
              <div className="api-endpoint-block" key={ep.path + ep.method}>
                <div className="api-endpoint-header">
                  <span className={`method method-${ep.method.toLowerCase()}`}>{ep.method}</span>
                  <span className="endpoint-path">{ep.path}</span>
                  <span className="endpoint-auth">{ep.auth}</span>
                </div>
                <div className="endpoint-desc">{ep.desc}</div>
                <div className="endpoint-params">
                  <b>Параметры:</b>
                  <ul>
                    {ep.params.map(p => (
                      <li key={p.name}><code>{p.name}</code> <span className="param-type">({p.type}{p.required ? ', обяз.' : ''})</span> — {p.desc}</li>
                    ))}
                  </ul>
                </div>
                <div className="endpoint-response">
                  <b>Ответ:</b>
                  <pre className="code-block">{ep.resp}</pre>
                </div>
              </div>
            ))}
          </section>
        )}
        {activeSection === 'examples' && (
          <section id="examples">
            <h2>Примеры кода</h2>
            <div className="code-examples-block">
              <h3>Загрузка файла (Python)</h3>
              <pre className="code-block">{PY_UPLOAD}</pre>
              <h3>Загрузка файла (JavaScript)</h3>
              <pre className="code-block">{JS_UPLOAD}</pre>
              <h3>Получение списка файлов (Python)</h3>
              <pre className="code-block">{PY_LIST}</pre>
              <h3>Получение списка файлов (JavaScript)</h3>
              <pre className="code-block">{JS_LIST}</pre>
              <h3>Получение информации о файле (Python)</h3>
              <pre className="code-block">{PY_GET}</pre>
              <h3>Получение информации о файле (JavaScript)</h3>
              <pre className="code-block">{JS_GET}</pre>
            </div>
          </section>
        )}
        {activeSection === 'faq' && (
          <section id="faq">
            <h2>FAQ</h2>
            <ul>
              <li><b>Какой максимальный размер файла?</b> — Зависит от тарифа: Standard — 50MB, Premium — 200MB, Pro — 1GB.</li>
              <li><b>Сколько файлов можно загрузить за раз?</b> — Зависит от тарифа: Standard — 5, Premium — 20, Pro — 100.</li>
              <li><b>Есть ли лимит на хранилище?</b> — Только для Standard и Premium. Pro — безлимитно.</li>
              <li><b>Какие типы файлов поддерживаются?</b> — Любые: изображения, видео, документы и др.</li>
              <li><b>Как получить прямую ссылку на файл?</b> — В ответе на загрузку файла будет URL.</li>
              <li><b>Какой формат ответа?</b> — Все ответы в JSON.</li>
              <li><b>Какой тип аутентификации использовать?</b> — Для файлов X-API-KEY, для статистики и логов — JWT.</li>
            </ul>
          </section>
        )}
      </main>
    </div>
  );
} 