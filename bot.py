/*
AWR — Assistant Work Resurs
React single-file WebApp for Telegram Mini App (preview / starter UI)

What's inside this file:
- A single-file React component (default export) using Tailwind classes
- Inline SVG logo (AWR) shown on app start
- Role-based UI: Admin, Brigada (crew), Kladovshchik (storeroom)
- Task list, filters, task editor modal, assign to brigada
- Brigada task view with multi-part report (comment, access, photo stub, materials)
- Inventory view for materials and tools with serial numbers
- Simple in-browser data store (mock) — replace with real backend API
- Excel/CSV export for the storeroom (downloads CSV)
- Telegram WebApp init hook (window.Telegram.WebApp) — used if opened inside Telegram

NOTE: This is a frontend *starter*. You still need a backend (e.g. Node.js + Express + Postgres/Mongo)
API suggestions (required):
  POST /api/auth/login               { telegramId, password } -> { token, role }
  GET  /api/tasks                    -> list tasks (query filters: status, brigada, address)
  POST /api/tasks                    -> create task
  PUT  /api/tasks/:id                -> update task (status, brigada, fields)
  DELETE /api/tasks/:id              -> delete task
  POST /api/tasks/:id/report         -> append partial report (part: 1..4)
  GET  /api/inventory                -> get warehouse inventory
  POST /api/inventory/adjust         -> add/remove inventory
  POST /api/tools/assign             -> assign tool (serial) to brigada
  POST /api/tools/return             -> return tool from brigada
  GET  /api/brigades                 -> list brigades and their holdings
  GET  /api/export/inventory         -> generate excel/csv (returns file)

Suggested DB schema (Postgres simplified):
  users(id, telegram_id, password_hash, role enum('admin','brigada','klad'), name)
  brigades(id, name, members jsonb)
  tasks(id, address, tz_text, access, note, brigade_id, status enum(...), created_by, created_at)
  reports(id, task_id, brigade_id, part int, payload jsonb, created_at)
  materials(id, name, unit enum('m','шт','кг'), total_amount numeric)
  warehouse(id, material_id, amount numeric)
  brigade_materials(id, brigade_id, material_id, amount numeric)
  tools(id, name, serial varchar unique, assigned_to_brigade_id nullable, status)

Security & files:
- Store photos on S3 or similar; store URL in report payload
- Use JWT for auth between frontend and backend
- Validate roles server-side

How to use this file:
- This is a React component suitable for inclusion in a small SPA built with Vite/CRA
- TailwindCSS classes used; include Tailwind in your build
- Replace mock API functions (api.*) with real fetch() calls to your backend

---------------------------------------------
*/

import React, { useEffect, useMemo, useState } from 'react'

// Mock initial data (replace with fetch from backend)
const INITIAL = {
  users: [
    { id: 1, telegramId: 111, password: 'adminpass', role: 'admin', name: 'Admin 1' },
    { id: 2, telegramId: 222, password: 'brig1pass', role: 'brigada', name: 'Brigada 1', brigadeId: 1 },
    { id: 3, telegramId: 333, password: 'kladpass', role: 'klad', name: 'Kladovshchik' }
  ],
  brigades: Array.from({ length: 10 }, (_, i) => ({ id: i+1, name: `Brigada ${i+1}`, members: [] })),
  materials: [
    { id: 'c_vok_4', name: 'Кабель ВОК 4', unit: 'м', total: 100 },
    { id: 'c_vok_8', name: 'Кабель ВОК 8', unit: 'м', total: 100 },
    { id: 'c_vok_12', name: 'Кабель ВОК 12', unit: 'м', total: 100 },
    { id: 'bo16', name: 'БО/16', unit: 'шт', total: 100 },
    { id: 'mufta_sq', name: 'Муфта (квадрат)', unit: 'шт', total: 100 },
    { id: 'gofra', name: 'Гофра', unit: 'м', total: 100 },
    { id: 'shpak', name: 'Шпаклёвка', unit: 'кг', total: 100 },
    { id: 'patch', name: 'Патчкорд', unit: 'шт', total: 100 }
  ],
  tools: [
    { id: 't1', name: 'перфоратор проводной', serial: 'SR-1001', assignedTo: null },
    { id: 't2', name: 'перфоратор беспроводной', serial: 'SR-1002', assignedTo: 1 }
  ],
  tasks: [
    { id: 1, address: 'ул. Ленина, 10', tz: 'Прокладка кабеля', access: 'с 9 до 18', note: '', brigadeId: 1, status: 'Новая задача', createdAt: Date.now() }
  ]
}

// --- Helper small components ---
function Logo({ className = 'w-16 h-16' }){
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg flex items-center justify-center">
        <svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="5" width="90" height="90" rx="18" fill="white" opacity="0.06" />
          <text x="50%" y="54%" textAnchor="middle" fontSize="28" fontWeight="700" fill="white">AWR</text>
        </svg>
      </div>
      <div className="hidden md:block">
        <div className="text-lg font-bold">AWR</div>
        <div className="text-sm text-slate-400">assistant work resurs</div>
      </div>
    </div>
  )
}

function Badge({ children }){
  return <span className="px-2 py-1 rounded-md bg-slate-100 text-slate-700 text-sm">{children}</span>
}

// --- Mock API (in-memory) ---
const api = (() => {
  let state = JSON.parse(JSON.stringify(INITIAL))
  let nextTaskId = 2
  return {
    login: async (telegramId, password) => {
      const u = state.users.find(x => x.telegramId === Number(telegramId) && x.password === password)
      if(!u) throw new Error('Неверный ID или пароль')
      return { token: 'mock-token', user: u }
    },
    getTasks: async (filters = {}) => {
      let res = state.tasks
      if(filters.status) res = res.filter(t => t.status === filters.status)
      if(filters.brigadeId) res = res.filter(t => t.brigadeId === Number(filters.brigadeId))
      if(filters.address) res = res.filter(t => t.address.includes(filters.address))
      return res
    },
    createTask: async (task) => {
      const t = { id: nextTaskId++, createdAt: Date.now(), status: 'Новая задача', ...task }
      state.tasks.push(t)
      return t
    },
    updateTask: async (id, patch) => {
      const t = state.tasks.find(x => x.id === Number(id))
      if(!t) throw new Error('Не найдено')
      Object.assign(t, patch)
      return t
    },
    deleteTask: async (id) => {
      state.tasks = state.tasks.filter(x => x.id !== Number(id))
      return true
    },
    getBrigades: async () => state.brigades,
    getInventory: async () => ({ materials: state.materials, tools: state.tools }),
    adjustMaterial: async (materialId, delta, brigadeId=null) => {
      const m = state.materials.find(x => x.id === materialId)
      if(!m) throw new Error('Material not found')
      m.total = (m.total || 0) + delta
      return m
    },
    assignTool: async (serial, brigadeId=null) => {
      const t = state.tools.find(x => x.serial === serial)
      if(!t) throw new Error('Tool not found')
      t.assignedTo = brigadeId
      return t
    }
  }
})()

// --- Main App ---
export default function AWRMiniApp(){
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState([])
  const [brigades, setBrigades] = useState([])
  const [inventory, setInventory] = useState({ materials: [], tools: [] })
  const [view, setView] = useState('dashboard')
  const [filters, setFilters] = useState({ status: '', brigadeId: '', address: '' })
  const [taskEditor, setTaskEditor] = useState(null)

  useEffect(() => {
    // Telegram WebApp init if present
    if(window.Telegram && window.Telegram.WebApp){
      try{ window.Telegram.WebApp.expand(); }catch(e){}
    }
  }, [])

  useEffect(() => { if(user){ fetchInitial() } }, [user])
  async function fetchInitial(){
    setLoading(true)
    const [tks, brs, inv] = await Promise.all([api.getTasks(), api.getBrigades(), api.getInventory()])
    setTasks(tks)
    setBrigades(brs)
    setInventory(inv)
    setLoading(false)
  }

  async function handleLogin({ telegramId, password }){
    try{
      setLoading(true)
      const res = await api.login(telegramId, password)
      setToken(res.token); setUser(res.user)
    }catch(e){ alert(e.message) }
    setLoading(false)
  }

  async function refreshTasks(){
    const t = await api.getTasks(filters)
    setTasks(t)
  }

  async function onCreateTask(payload){
    await api.createTask(payload)
    await refreshTasks()
    setTaskEditor(null)
  }

  async function onUpdateTask(id, patch){
    await api.updateTask(id, patch)
    await refreshTasks()
  }

  async function exportInventoryCSV(){
    const rows = []
    rows.push(['Материал/Инструмент','Тип','Единица/серия','Остаток'])
    inventory.materials.forEach(m => rows.push([m.name, 'Материал', m.unit, m.total]))
    inventory.tools.forEach(t => rows.push([t.name, 'Инструмент', t.serial, t.assignedTo ? ('Бриг ' + t.assignedTo) : 'На складе']))
    const csv = rows.map(r => r.map(c => '"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'awr_inventory.csv'; a.click(); URL.revokeObjectURL(url)
  }

  if(!user) return <Auth onLogin={handleLogin} loading={loading} />

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Logo />
          <div>
            <div className="text-sm text-slate-500">Пользователь</div>
            <div className="font-semibold">{user.name} <Badge>{user.role}</Badge></div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-3 py-2 rounded-md bg-white shadow-sm" onClick={() => { setUser(null); setToken(null) }}>Выйти</button>
        </div>
      </header>

      <div className="grid md:grid-cols-4 gap-6">
        <nav className="md:col-span-1 bg-white rounded-2xl p-4 shadow-sm">
          <div className="text-sm font-medium mb-3">Меню</div>
          <div className="flex flex-col gap-2">
            {user.role === 'admin' && (
              <>
                <NavBtn onClick={() => setView('tasks')}>Активные задачи</NavBtn>
                <NavBtn onClick={() => setTaskEditor({})}>Назначить задачу</NavBtn>
                <NavBtn onClick={() => setView('brigade_materials')}>Материалы у бригад</NavBtn>
                <NavBtn onClick={() => setView('brigade_tools')}>Инструмент у бригад</NavBtn>
                <NavBtn onClick={() => setView('warehouse')}>Остатки по складу</NavBtn>
              </>
            )}

            {user.role === 'brigada' && (
              <>
                <NavBtn onClick={() => setView('my_tasks')}>Мои задачи</NavBtn>
                <NavBtn onClick={() => setView('done')}>Выполненные</NavBtn>
                <NavBtn onClick={() => setView('postponed')}>Отложенные</NavBtn>
                <NavBtn onClick={() => setView('problem')}>Проблемные дома</NavBtn>
                <NavBtn onClick={() => setView('my_materials')}>Мои материалы</NavBtn>
                <NavBtn onClick={() => setView('my_tools')}>Мой инструмент</NavBtn>
              </>
            )}

            {user.role === 'klad' && (
              <>
                <NavBtn onClick={() => setView('issue_material')}>Выдать материал</NavBtn>
                <NavBtn onClick={() => setView('receive_material')}>Принять материал</NavBtn>
                <NavBtn onClick={() => setView('move_material')}>Переместить материал</NavBtn>
                <NavBtn onClick={() => setView('issue_tool')}>Выдать инструмент</NavBtn>
                <NavBtn onClick={() => setView('receive_tool')}>Принять инструмент</NavBtn>
                <NavBtn onClick={() => setView('restock')}>Пополнить склад</NavBtn>
                <NavBtn onClick={() => setView('warehouse')}>Остатки по складу</NavBtn>
              </>
            )}

          </div>
        </nav>

        <main className="md:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">{viewTitle(view)}</h2>
            <div className="flex items-center gap-2">
              <button onClick={refreshTasks} className="px-3 py-1 rounded-md bg-white shadow">Обновить</button>
              {user.role === 'klad' && <button onClick={exportInventoryCSV} className="px-3 py-1 rounded-md bg-indigo-600 text-white">Выгрузить Excel</button>}
            </div>
          </div>

          <div className="space-y-4">
            {view === 'dashboard' && (
              <div className="grid md:grid-cols-2 gap-4">
                <Card>
                  <div className="text-sm text-slate-500">Задачи</div>
                  <div className="mt-3">
                    <div className="text-3xl font-bold">{tasks.length}</div>
                    <div className="text-sm text-slate-400">Всего активных задач</div>
                  </div>
                </Card>
                <Card>
                  <div className="text-sm text-slate-500">Остатки на складе</div>
                  <div className="mt-3">
                    <div className="text-3xl font-bold">{inventory.materials.length}</div>
                    <div className="text-sm text-slate-400">Видов материалов</div>
                  </div>
                </Card>
              </div>
            )}

            {view === 'tasks' && (
              <div>
                <FilterBar filters={filters} setFilters={setFilters} onApply={refreshTasks} brigades={brigades} />
                <TaskList tasks={tasks} onEdit={(t)=>setTaskEditor(t)} onUpdate={onUpdateTask} onDelete={async id=>{ if(confirm('Удалить?')){ await api.deleteTask(id); refreshTasks() } }} />
              </div>
            )}

            {view === 'my_tasks' && (
              <TaskList tasks={tasks.filter(t=>t.brigadeId===user.brigadeId)} onEdit={(t)=>setTaskEditor(t)} onUpdate={onUpdateTask} />
            )}

            {view === 'warehouse' && (
              <Card>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <div className="font-medium mb-2">Материалы (склад)</div>
                    <table className="w-full text-sm">
                      <thead><tr><th className="text-left">Материал</th><th>Ед.</th><th>Остаток</th></tr></thead>
                      <tbody>
                        {inventory.materials.map(m => (
                          <tr key={m.id}><td>{m.name}</td><td className="text-center">{m.unit}</td><td className="text-right">{m.total}</td></tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div>
                    <div className="font-medium mb-2">Инструмент</div>
                    <table className="w-full text-sm">
                      <thead><tr><th className="text-left">Инструмент</th><th>Серийный</th><th>Статус</th></tr></thead>
                      <tbody>
                        {inventory.tools.map(t => (
                          <tr key={t.id}><td>{t.name}</td><td>{t.serial}</td><td>{t.assignedTo ? 'У бригады '+t.assignedTo : 'На складе'}</td></tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            )}

            {taskEditor && <TaskEditor brigades={brigades} task={taskEditor} onClose={()=>setTaskEditor(null)} onSave={onCreateTask} onUpdate={onUpdateTask} />}

            {/* Add other views as needed (my_materials, my_tools, store operations) - left as exercise to wire to API */}

          </div>
        </main>
      </div>
    </div>
  )
}

// --- Small UI pieces ---
function NavBtn({ children, onClick }){
  return <button onClick={onClick} className="text-left px-3 py-2 rounded-lg hover:bg-slate-50">{children}</button>
}
function Card({ children }){ return <div className="bg-white p-4 rounded-2xl shadow-sm">{children}</div> }

function viewTitle(v){
  switch(v){
    case 'dashboard': return 'Панель';
    case 'tasks': return 'Активные задачи';
    case 'my_tasks': return 'Мои задачи';
    case 'warehouse': return 'Остатки по складу';
    default: return 'AWR'
  }
}

function Auth({ onLogin, loading }){
  const [tgId, setTgId] = useState('')
  const [pwd, setPwd] = useState('')
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-50 to-white p-4">
      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-lg p-8">
        <div className="flex items-center gap-6 mb-6">
          <Logo className="w-44" />
          <div>
            <h1 className="text-2xl font-bold">AWR — Вход</h1>
            <div className="text-sm text-slate-400">Авторизуйтесь по Telegram ID и паролю</div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm">Telegram ID</label>
            <input value={tgId} onChange={e=>setTgId(e.target.value)} className="w-full mt-2 p-3 border rounded-md" placeholder="Например 123456" />
          </div>
          <div>
            <label className="text-sm">Пароль</label>
            <input value={pwd} onChange={e=>setPwd(e.target.value)} type="password" className="w-full mt-2 p-3 border rounded-md" placeholder="Ваш пароль" />
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-slate-400">Авторизация через бота открывает это мини-приложение</div>
          <div>
            <button onClick={()=>onLogin({ telegramId: tgId, password: pwd })} className="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow">{loading ? 'Загрузка...' : 'Войти'}</button>
          </div>
        </div>
      </div>
    </div>
  )
}

function FilterBar({ filters, setFilters, onApply, brigades }){
  return (
    <div className="bg-white p-3 rounded-xl flex items-center gap-3">
      <select value={filters.status} onChange={e=>setFilters(f=>({...f, status: e.target.value}))} className="p-2 border rounded">
        <option value="">Все статусы</option>
        <option>Новая задача</option>
        <option>В работе</option>
        <option>Выполнено</option>
        <option>Отложено</option>
        <option>Проблемный дом</option>
      </select>
      <select value={filters.brigadeId} onChange={e=>setFilters(f=>({...f, brigadeId: e.target.value}))} className="p-2 border rounded">
        <option value="">Все бригады</option>
        {brigades.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
      </select>
      <input value={filters.address} onChange={e=>setFilters(f=>({...f, address: e.target.value}))} placeholder="Адрес" className="p-2 border rounded flex-1" />
      <button onClick={onApply} className="px-3 py-2 bg-indigo-600 text-white rounded">Применить</button>
    </div>
  )
}

function TaskList({ tasks, onEdit, onUpdate, onDelete }){
  return (
    <div className="space-y-3">
      {tasks.map(t => (
        <div key={t.id} className="bg-white p-4 rounded-xl shadow-sm flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="font-medium">{t.address}</div>
              <div className="text-sm text-slate-400">{t.tz}</div>
              <Badge>{t.status}</Badge>
            </div>
            <div className="text-sm text-slate-500 mt-2">Доступ: {t.access} | Бригада: {t.brigadeId || 'не назначена'}</div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={()=>onEdit(t)} className="px-3 py-1 border rounded">Редактировать</button>
            <button onClick={()=>onUpdate(t.id, { status: 'В работе' })} className="px-3 py-1 bg-yellow-200 rounded">В работу</button>
            <button onClick={()=>onUpdate(t.id, { status: 'Выполнено' })} className="px-3 py-1 bg-green-200 rounded">Выполнено</button>
            {onDelete && <button onClick={()=>onDelete(t.id)} className="px-3 py-1 bg-red-100 rounded">Удалить</button>}
          </div>
        </div>
      ))}
    </div>
  )
}

function TaskEditor({ task, brigades, onClose, onSave, onUpdate }){
  const isNew = !task || !task.id
  const [address, setAddress] = useState(task?.address || '')
  const [tz, setTz] = useState(task?.tz || '')
  const [access, setAccess] = useState(task?.access || '')
  const [note, setNote] = useState(task?.note || '')
  const [brigadeId, setBrigadeId] = useState(task?.brigadeId || '')

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="font-semibold">{isNew ? 'Создать задачу' : 'Редактировать задачу'}</div>
          <div className="text-sm text-slate-500">ID: {task?.id || 'новая'}</div>
        </div>
        <div className="grid md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm">Адрес</label>
            <input value={address} onChange={e=>setAddress(e.target.value)} className="w-full p-2 border rounded mt-1" />
          </div>
          <div>
            <label className="text-sm">Бригада</label>
            <select value={brigadeId} onChange={e=>setBrigadeId(e.target.value)} className="w-full p-2 border rounded mt-1">
              <option value="">Без назначений</option>
              {brigades.map(b=> <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="text-sm">ТЗ</label>
            <textarea value={tz} onChange={e=>setTz(e.target.value)} className="w-full p-2 border rounded mt-1" rows={3} />
          </div>
          <div>
            <label className="text-sm">Доступ</label>
            <input value={access} onChange={e=>setAccess(e.target.value)} className="w-full p-2 border rounded mt-1" />
          </div>
          <div>
            <label className="text-sm">Пометка</label>
            <input value={note} onChange={e=>setNote(e.target.value)} className="w-full p-2 border rounded mt-1" />
          </div>
        </div>

        <div className="mt-4 flex items-center justify-end gap-3">
          <button onClick={onClose} className="px-3 py-2">Отмена</button>
          {isNew ? (
            <button onClick={()=>onSave({ address, tz, access, note, brigadeId: brigadeId ? Number(brigadeId) : null })} className="px-4 py-2 bg-indigo-600 text-white rounded">Создать</button>
          ) : (
            <button onClick={()=>onUpdate(task.id, { address, tz, access, note, brigadeId: brigadeId ? Number(brigadeId) : null })} className="px-4 py-2 bg-indigo-600 text-white rounded">Сохранить</button>
          )}
        </div>
      </div>
    </div>
  )
}

