import { useEffect, useState } from 'react'
import { ArrowDownRight, ArrowLeft, ArrowRight, Check, ChevronDown, Clock3, Flame, Leaf, LogIn, LogOut, Minus, Plus, ShoppingBag, UserRound, X } from 'lucide-react'

type User = { id: number; nome: string; email: string; admin: boolean }
type OrderItem = { id: number; sabor: string; tamanho: string; quantidade: number; preco: number }
type Order = { id: number; status: string; preco: number; itens: OrderItem[] }
type Pizza = { name: string; description: string; category: string; image: string; prices: Record<string, number>; tag?: string; vegetarian?: boolean }
type CartEntry = { pizza: Pizza; size: string; quantity: number }

const API = ''
const TOKEN_KEY = 'forno-access-token'
const sizes = ['P', 'M', 'G']
const pizzas: Pizza[] = [
  { name: 'Margherita', description: 'Tomate italiano, fior di latte, manjericão fresco e azeite.', category: 'Clássicas', image: 'https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=900&q=85', prices: { P: 32, M: 42, G: 54 }, tag: 'A casa', vegetarian: true },
  { name: 'Diavola', description: 'Salame picante, mozzarella cremosa e mel de pimenta.', category: 'Autorais', image: 'https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=900&q=85', prices: { P: 38, M: 49, G: 62 }, tag: 'Picante', },
  { name: 'Quattro Formaggi', description: 'Gorgonzola, parmesão, provolone e mozzarella.', category: 'Clássicas', image: 'https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=900&q=85', prices: { P: 37, M: 48, G: 60 }, vegetarian: true },
  { name: 'Funghi', description: 'Cogumelos tostados, tomilho, alho confitado e creme de ricota.', category: 'Da horta', image: 'https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?auto=format&fit=crop&w=900&q=85', prices: { P: 36, M: 47, G: 59 }, tag: 'Vegetariana', vegetarian: true },
  { name: 'Pepperoni', description: 'Pepperoni artesanal, mozzarella e orégano da Sicília.', category: 'Clássicas', image: 'https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=900&q=85', prices: { P: 35, M: 46, G: 58 } },
  { name: 'Prosciutto', description: 'Presunto curado, rúcula selvagem e lascas de parmesão.', category: 'Autorais', image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=85', prices: { P: 39, M: 51, G: 64 }, tag: 'Favorita' },
]

const money = (value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)

async function api<T>(path: string, init: RequestInit = {}, token = localStorage.getItem(TOKEN_KEY)): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API}${path}`, { ...init, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || 'Algo deu errado. Tente novamente.')
  }
  return response.json() as Promise<T>
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [orders, setOrders] = useState<Order[]>([])
  const [cart, setCart] = useState<CartEntry[]>([])
  const [selectedSizes, setSelectedSizes] = useState<Record<string, string>>({})
  const [activeCategory, setActiveCategory] = useState('Tudo')
  const [activeView, setActiveView] = useState<'menu' | 'orders'>('menu')
  const [cartOpen, setCartOpen] = useState(false)
  const [accountOpen, setAccountOpen] = useState(false)
  const [registerMode, setRegisterMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return
    api<User>('/auth/me', {}, token).then(setUser).catch(() => localStorage.removeItem(TOKEN_KEY))
  }, [])

  useEffect(() => {
    if (!user) return
    api<Order[]>('/pedidos/').then(setOrders).catch(() => setMessage('Não foi possível carregar seus pedidos.'))
  }, [user])

  const categories = ['Tudo', 'Clássicas', 'Autorais', 'Da horta']
  const visiblePizzas = activeCategory === 'Tudo' ? pizzas : pizzas.filter((pizza) => pizza.category === activeCategory)
  const cartCount = cart.reduce((sum, entry) => sum + entry.quantity, 0)
  const cartTotal = cart.reduce((sum, entry) => sum + entry.pizza.prices[entry.size] * entry.quantity, 0)

  function addToCart(pizza: Pizza) {
    const size = selectedSizes[pizza.name] || 'M'
    setCart((current) => {
      const existing = current.find((entry) => entry.pizza.name === pizza.name && entry.size === size)
      if (existing) return current.map((entry) => entry === existing ? { ...entry, quantity: entry.quantity + 1 } : entry)
      return [...current, { pizza, size, quantity: 1 }]
    })
    setMessage(`${pizza.name} adicionada ao pedido`)
    window.setTimeout(() => setMessage(''), 2400)
  }

  function changeQuantity(index: number, delta: number) {
    setCart((current) => current.map((entry, itemIndex) => itemIndex === index ? { ...entry, quantity: entry.quantity + delta } : entry).filter((entry) => entry.quantity > 0))
  }

  async function loadOrders() {
    const result = await api<Order[]>('/pedidos/')
    setOrders(result)
  }

  async function submitAccount(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      if (registerMode) await api<User>('/auth/criar_conta', { method: 'POST', body: JSON.stringify({ nome: name, email, senha: password, ativo: true, admin: false }) }, null)
      const token = await api<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, senha: password }) }, null)
      localStorage.setItem(TOKEN_KEY, token.access_token)
      const currentUser = await api<User>('/auth/me', {}, token.access_token)
      setUser(currentUser)
      setAccountOpen(false)
      setPassword('')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Não foi possível acessar sua conta.')
    } finally {
      setLoading(false)
    }
  }

  async function checkout() {
    if (!user) {
      setCartOpen(false)
      setAccountOpen(true)
      setMessage('Entre na sua conta para finalizar o pedido.')
      return
    }
    setLoading(true)
    try {
      await api<Order>('/pedidos/', { method: 'POST', body: JSON.stringify({ status: 'PENDENTE', itens: cart.map(({ pizza, size, quantity }) => ({ sabor: pizza.name, tamanho: size, quantidade: quantity, preco: pizza.prices[size] })) }) })
      setCart([])
      setCartOpen(false)
      setActiveView('orders')
      await loadOrders()
      setMessage('Pedido enviado para a cozinha.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Não foi possível enviar o pedido.')
    } finally {
      setLoading(false)
    }
  }

  function signOut() {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
    setOrders([])
    setActiveView('menu')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="wordmark" href="#inicio" onClick={() => setActiveView('menu')} aria-label="Forno, início"><span className="brand-mark">F<span>.</span></span><span>FORNO<br /><small>PIZZERIA</small></span></a>
        <nav className="main-nav" aria-label="Navegação principal">
          <button className={activeView === 'menu' ? 'nav-link is-active' : 'nav-link'} onClick={() => setActiveView('menu')}>Cardápio</button>
          <button className={activeView === 'orders' ? 'nav-link is-active' : 'nav-link'} onClick={() => user ? setActiveView('orders') : setAccountOpen(true)}>Meus pedidos</button>
        </nav>
        <div className="top-actions">
          {user ? <button className="account-button" onClick={signOut} title="Sair"><span className="avatar">{user.nome.slice(0, 1).toUpperCase()}</span><span className="account-name">{user.nome.split(' ')[0]}</span><LogOut size={16} /></button> : <button className="account-button" onClick={() => setAccountOpen(true)}><UserRound size={17} /><span>Entrar</span></button>}
          <button className="cart-button" onClick={() => setCartOpen(true)} aria-label={`Abrir sacola, ${cartCount} itens`}><ShoppingBag size={18} /><span>Sacola</span><b>{cartCount}</b></button>
        </div>
      </header>

      <main>
        {activeView === 'menu' ? <>
          <section className="hero" id="inicio">
            <div className="hero-copy">
              <p className="eyebrow"><span /> FEITA DEVAGAR. COMIDA QUENTE.</p>
              <h1>Uma boa pizza<br />muda <em>a noite.</em></h1>
              <p className="hero-description">Massa de longa fermentação, ingredientes honestos e o forno sempre aceso. O resto é conversa.</p>
              <button className="hero-cta" onClick={() => document.getElementById('cardapio')?.scrollIntoView({ behavior: 'smooth' })}>Escolha a sua <ArrowDownRight size={17} /></button>
              <div className="hero-meta"><span><Clock3 size={15} /> 30–45 min</span><i /><span>Forno a lenha, desde 2014</span></div>
            </div>
            <div className="hero-image" role="img" aria-label="Pizza artesanal saindo do forno"><div className="hero-stamp"><span>FERMENTAÇÃO</span><strong>48h</strong><span>SEM PRESSA.</span></div><div className="hero-caption"><span>01 / NOSSA MASSA</span><span>NAPOLITANA, À NOSSA MANEIRA</span></div></div>
            <div className="hero-index">01 <span>/</span> 03</div>
          </section>

          <section className="menu-section" id="cardapio">
            <div className="section-heading"><div><p className="eyebrow">O CARDÁPIO</p><h2>Do forno, <em>com afeto.</em></h2></div><p className="menu-note">Cada pizza começa com farinha, água<br />e um pouco de paciência.</p></div>
            <div className="menu-toolbar"><div className="filters" role="tablist" aria-label="Filtrar pizzas">{categories.map((category) => <button key={category} role="tab" aria-selected={activeCategory === category} className={activeCategory === category ? 'filter is-selected' : 'filter'} onClick={() => setActiveCategory(category)}>{category}</button>)}</div><span className="item-count">{visiblePizzas.length} PIZZAS</span></div>
            <div className="pizza-grid">{visiblePizzas.map((pizza, index) => <article className="pizza-card" key={pizza.name} style={{ animationDelay: `${index * 70}ms` }}>
              <div className="pizza-image-wrap"><img className="pizza-image" src={pizza.image} alt={`Pizza ${pizza.name}`} loading="lazy" />{pizza.tag && <span className="pizza-tag">{pizza.tag}</span>}<span className="pizza-number">0{pizzas.indexOf(pizza) + 1}</span></div>
              <div className="pizza-info"><div className="pizza-title-row"><h3>{pizza.name}</h3>{pizza.vegetarian && <Leaf size={15} aria-label="Vegetariana" />}</div><p>{pizza.description}</p><div className="pizza-controls"><label className="size-select"><span className="sr-only">Tamanho da pizza {pizza.name}</span><select value={selectedSizes[pizza.name] || 'M'} onChange={(event) => setSelectedSizes((current) => ({ ...current, [pizza.name]: event.target.value }))}>{sizes.map((size) => <option key={size} value={size}>{size}</option>)}</select><ChevronDown size={13} /></label><strong>{money(pizza.prices[selectedSizes[pizza.name] || 'M'])}</strong><button className="add-button" onClick={() => addToCart(pizza)} aria-label={`Adicionar ${pizza.name} ao pedido`}><Plus size={17} /></button></div></div>
            </article>)}</div>
          </section>
          <section className="closing-band"><Flame size={20} /><p>O forno não tem pressa.<br /><em>Você também não precisa ter.</em></p><span>ABERTO HOJE · 18H — 23H</span></section>
        </> : <section className="orders-section"><div className="section-heading"><div><p className="eyebrow">SUA CONTA</p><h2>O caminho da <em>sua pizza.</em></h2></div><button className="text-link" onClick={() => setActiveView('menu')}><ArrowLeft size={16} /> Voltar ao cardápio</button></div>{orders.length ? <div className="orders-list">{[...orders].reverse().map((order) => <article className="order-row" key={order.id}><div className="order-number"><span>PEDIDO</span><strong>#{String(order.id).padStart(4, '0')}</strong></div><div className="order-items">{order.itens.map((item) => <span key={item.id}>{item.quantidade}× {item.sabor} <small>({item.tamanho})</small></span>)}</div><span className={`order-status status-${order.status.toLowerCase()}`}><i />{order.status.replace('_', ' ')}</span><strong className="order-price">{money(order.preco)}</strong></article>)}</div> : <div className="empty-orders"><ShoppingBag size={24} /><h3>Ainda não tem pedido por aqui.</h3><p>Escolha uma pizza e a gente cuida do resto.</p><button className="hero-cta" onClick={() => setActiveView('menu')}>Ver o cardápio <ArrowRight size={16} /></button></div>}</section>}
      </main>

      <footer className="footer"><a className="wordmark footer-mark" href="#inicio"><span className="brand-mark">F<span>.</span></span><span>FORNO<br /><small>PIZZERIA</small></span></a><span>FARINHA · ÁGUA · TEMPO</span><span>FEITO COM CALMA, EM SÃO PAULO.</span></footer>

      {message && <div className="toast" role="status"><Check size={16} />{message}<button onClick={() => setMessage('')} aria-label="Fechar aviso"><X size={14} /></button></div>}

      {cartOpen && <div className="overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) setCartOpen(false) }}><aside className="drawer" aria-label="Sua sacola"><div className="drawer-header"><div><p className="eyebrow">SEU PEDIDO</p><h2>Sacola <em>({cartCount})</em></h2></div><button className="icon-button" onClick={() => setCartOpen(false)} aria-label="Fechar sacola"><X size={20} /></button></div>{cart.length ? <><div className="cart-lines">{cart.map((entry, index) => <div className="cart-line" key={`${entry.pizza.name}-${entry.size}`}><img src={entry.pizza.image} alt="" /><div className="cart-line-info"><strong>{entry.pizza.name}</strong><span>Tamanho {entry.size} · {money(entry.pizza.prices[entry.size])}</span><div className="quantity-control"><button onClick={() => changeQuantity(index, -1)} aria-label="Diminuir quantidade"><Minus size={13} /></button><span>{entry.quantity}</span><button onClick={() => changeQuantity(index, 1)} aria-label="Aumentar quantidade"><Plus size={13} /></button></div></div><strong className="line-total">{money(entry.pizza.prices[entry.size] * entry.quantity)}</strong></div>)}</div><div className="cart-summary"><div><span>Subtotal</span><strong>{money(cartTotal)}</strong></div><small>Entrega calculada no próximo passo.</small><button className="checkout-button" onClick={checkout} disabled={loading}>{loading ? 'Enviando...' : user ? 'Enviar para a cozinha' : 'Entrar e continuar'}<ArrowRight size={17} /></button><button className="continue-link" onClick={() => setCartOpen(false)}>Continuar escolhendo</button></div></> : <div className="empty-cart"><ShoppingBag size={25} /><h3>Sua sacola está vazia.</h3><p>Uma boa escolha muda a noite.</p><button className="hero-cta" onClick={() => setCartOpen(false)}>Explorar o cardápio <ArrowRight size={16} /></button></div>}</aside></div>}

      {accountOpen && <div className="overlay account-overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) setAccountOpen(false) }}><section className="account-modal" aria-label={registerMode ? 'Criar conta' : 'Entrar na conta'}><div className="modal-top"><span className="eyebrow">FORNO PIZZERIA</span><button className="icon-button" onClick={() => setAccountOpen(false)} aria-label="Fechar"><X size={19} /></button></div><h2>{registerMode ? <>Chegue mais <em>perto.</em></> : <>Que bom <em>te ver.</em></>}</h2><p className="modal-description">{registerMode ? 'Crie sua conta para acompanhar cada pedido.' : 'Entre para acompanhar sua próxima pizza.'}</p><form onSubmit={submitAccount} className="account-form">{registerMode && <label>Seu nome<input required autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Como podemos te chamar?" /></label>}<label>E-mail<input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="voce@email.com" /></label><label>Senha<input type="password" required minLength={6} autoComplete={registerMode ? 'new-password' : 'current-password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Mínimo de 6 caracteres" /></label><button className="checkout-button" disabled={loading}>{loading ? 'Só um instante...' : registerMode ? 'Criar conta' : 'Entrar'}<LogIn size={17} /></button></form><p className="switch-account">{registerMode ? 'Já tem uma conta?' : 'Ainda não conhece a casa?'} <button onClick={() => { setRegisterMode(!registerMode); setMessage('') }}>{registerMode ? 'Entrar' : 'Criar conta'}</button></p></section></div>}
    </div>
  )
}

export default App
