/* ============================================
   Hermes News — Application Logic
   No API key required — rss2json + mock fallback
   ============================================ */

// ============================================
// 1. Configuration
// ============================================
const CONFIG = {
  refreshInterval: 300000,   // 5 min
  cacheTTL: 600000,          // 10 min
  cacheKey: 'hermes_news_v2',
  themeKey: 'hermes_theme',
  fetchTimeout: 10000,       // 10s per feed
  maxArticles: 50,
  tickerCount: 15,
  rssBase: 'https://api.rss2json.com/v1/api.json',
  animStagger: 60,           // ms between card fade-ins
}

// ============================================
// 2. RSS Feeds
// ============================================
const RSS_FEEDS = [
  { id: 'keji-36kr',    name: '36氪',       url: 'https://36kr.com/feed',                  category: 'tech',    lang: 'zh' },
  { id: 'keji-hn',      name: 'Hacker News', url: 'https://hnrss.org/frontpage',          category: 'tech',    lang: 'en' },
  { id: 'guoji-zaobao', name: '联合早报',    url: 'https://www.zaobao.com.sg/news.rss',     category: 'world',   lang: 'zh' },
]

// ============================================
// 3. Mock Data (built-in fallback)
// ============================================
function buildMockData () {
  const now = Date.now()
  const h = n => now - n * 3600000

  const articles = [
    // --- 科技 (tech) ---
    {
      id: 'mock-t1', title: '人工智能新突破：新一代大语言模型发布，推理能力大幅提升',
      desc: '今日召开的AI开发者大会上，研究团队公布了最新一代大语言模型，在数学推理、代码生成和多轮对话等多项基准测试中表现优异，性能较前代提升超过40%。专家表示这标志着通用人工智能迈出了重要一步。',
      image: 'https://picsum.photos/seed/aibreak/800/450', source: 'Mock 科技',
      time: h(2), category: 'tech', url: '#',
    },
    {
      id: 'mock-t2', title: '智能手机市场格局生变，折叠屏出货量同比增长180%',
      desc: '调研机构最新数据显示，2025年第一季度全球折叠屏手机出货量同比增长180%，市场份额首次突破15%。多家厂商推出轻薄化折叠新品，价格下探至5000元价位段，推动渗透率快速提升。',
      image: 'https://picsum.photos/seed/foldphone/800/450', source: 'Mock 科技',
      time: h(4), category: 'tech', url: '#',
    },
    {
      id: 'mock-t3', title: '量子计算里程碑：全球首台千比特量子计算机问世',
      desc: '科研团队成功研发出搭载1024个量子比特的量子计算机，实现了对经典超级计算机的量子优越性。该计算机在药物分子模拟和组合优化等特定问题上展现出革命性的计算能力。',
      image: 'https://picsum.photos/seed/quantum/800/450', source: 'Mock 科技',
      time: h(7), category: 'tech', url: '#',
    },
    {
      id: 'mock-t4', title: '自动驾驶商业化提速，无人出租覆盖全国十城',
      desc: '自动驾驶企业宣布无人驾驶出租车服务已扩展至全国10个主要城市，累计完成超过500万次安全载客行程。同时，L4级自动驾驶物流车也在多个城市开启常态化运营。',
      image: 'https://picsum.photos/seed/autodrive/800/450', source: 'Mock 科技',
      time: h(10), category: 'tech', url: '#',
    },
    {
      id: 'mock-t5', title: '国产芯片制程获重大突破，3纳米工艺试产成功',
      desc: '国内半导体企业宣布其自主研发的3纳米制程工艺已完成试产，良率达到预期水平。这标志着我国在先进芯片制造领域迈出关键一步，将有效缓解高端芯片供应紧张局面。',
      image: 'https://picsum.photos/seed/chip/800/450', source: 'Mock 科技',
      time: h(14), category: 'tech', url: '#',
    },
    {
      id: 'mock-t6', title: 'VR头显销量爆发式增长，生态内容数量翻倍',
      desc: '2025年第二季度全球VR头显出货量同比增长210%，首次突破千万台大关。随着苹果、Meta等厂商推出新一代产品，VR内容生态也迎来爆发，应用数量较去年同期增长120%。',
      image: 'https://picsum.photos/seed/vr/800/450', source: 'Mock 科技',
      time: h(18), category: 'tech', url: '#',
    },
    {
      id: 'mock-t7', title: '云计算价格战再升级，三大厂商推出全新折扣方案',
      desc: '阿里云、腾讯云、华为云相继宣布新一轮降价，核心计算产品降幅最高达35%。业内分析认为，AI算力需求爆发和规模化效应是降价的主要驱动力，中小企业和开发者成为最大受益方。',
      image: 'https://picsum.photos/seed/cloud/800/450', source: 'Mock 科技',
      time: h(22), category: 'tech', url: '#',
    },
    {
      id: 'mock-t8', title: '新型勒索病毒全球蔓延，多国联合发布预警',
      desc: '一种新型勒索病毒正在全球范围内快速传播，已感染超过20个国家的关键基础设施。网络安全机构紧急发布补丁和防御指南，建议企业和个人立即更新系统并备份重要数据。',
      image: 'https://picsum.photos/seed/cyber/800/450', source: 'Mock 科技',
      time: h(26), category: 'tech', url: '#',
    },

    // --- 国际 (world) ---
    {
      id: 'mock-w1', title: '联合国气候大会达成历史性协议，195国承诺减排新目标',
      desc: '经过两周的艰难谈判，联合国气候变化大会最终达成新的全球气候协议。195个缔约方承诺在2035年前将温室气体排放量减少50%，并设立1000亿美元气候基金支持发展中国家。',
      image: 'https://picsum.photos/seed/climate/800/450', source: 'Mock 国际',
      time: h(3), category: 'world', url: '#',
    },
    {
      id: 'mock-w2', title: '全球经济复苏分化明显，新兴市场增速领跑',
      desc: '国际货币基金组织发布最新《世界经济展望》报告，上调新兴市场经济体增长预期至4.8%，但同时下调发达经济体增速至1.5%。报告指出通胀压力和地缘政治风险仍是主要挑战。',
      image: 'https://picsum.photos/seed/economy/800/450', source: 'Mock 国际',
      time: h(6), category: 'world', url: '#',
    },
    {
      id: 'mock-w3', title: '中东和平进程取得突破，多方签署框架协议',
      desc: '在国际社会斡旋下，中东地区多方代表在日内瓦签署和平框架协议，就停火、人道主义援助和重建达成共识。联合国秘书长表示这是"多年来最具希望的和谈进展"。',
      image: 'https://picsum.photos/seed/peace/800/450', source: 'Mock 国际',
      time: h(9), category: 'world', url: '#',
    },
    {
      id: 'mock-w4', title: '多国联合公布月球基地建设计划，2030年前建成',
      desc: '美国、中国、欧盟等航天机构联合公布了国际月球科研站建设路线图，计划在2030年前完成基本构型建设。项目将分三个阶段推进，最终实现月面长期驻留和资源利用。',
      image: 'https://picsum.photos/seed/moon/800/450', source: 'Mock 国际',
      time: h(13), category: 'world', url: '#',
    },
    {
      id: 'mock-w5', title: '极端天气频发威胁全球粮食安全，多国启动应急储备',
      desc: '受厄尔尼诺现象影响，全球多地遭遇极端高温和干旱，主要粮食产区产量预计下降15%。世界粮食计划署警告超过3亿人面临粮食不安全风险，多国已启动战略粮食储备。',
      image: 'https://picsum.photos/seed/food/800/450', source: 'Mock 国际',
      time: h(17), category: 'world', url: '#',
    },
    {
      id: 'mock-w6', title: '国际移民潮持续升温，各国调整边境政策',
      desc: '全球移民人数突破3亿大关，多国政府纷纷调整移民政策。加拿大、澳大利亚等传统移民国家提高技术移民配额，欧洲多国则加强边境管控，引发国际社会对难民权利的关注。',
      image: 'https://picsum.photos/seed/migration/800/450', source: 'Mock 国际',
      time: h(21), category: 'world', url: '#',
    },

    // --- 商业 (business) ---
    {
      id: 'mock-b1', title: '央行宣布降息25个基点，释放流动性支持实体经济',
      desc: '中国人民银行宣布下调中期借贷便利利率25个基点，同时引导贷款市场报价利率下行。专家分析此次降息旨在降低企业融资成本，支持实体经济复苏，预计释放长期流动性约8000亿元。',
      image: 'https://picsum.photos/seed/rate/800/450', source: 'Mock 商业',
      time: h(1), category: 'business', url: '#',
    },
    {
      id: 'mock-b2', title: '新能源汽车出口再创新高，自主品牌加速全球布局',
      desc: '海关总署数据显示，2025年上半年我国新能源汽车出口量突破120万辆，同比增长65%。比亚迪、蔚来等品牌在东南亚、欧洲市场销量大幅增长，多款车型进入当地销量前十。',
      image: 'https://picsum.photos/seed/ev/800/450', source: 'Mock 商业',
      time: h(5), category: 'business', url: '#',
    },
    {
      id: 'mock-b3', title: '数字人民币跨境支付落地，覆盖东盟十国',
      desc: '数字人民币跨境支付系统正式在东盟十国上线运行，实现与当地主流支付工具的互联互通。首批试点涵盖贸易结算、旅游消费和汇款等场景，日均交易额已突破10亿元。',
      image: 'https://picsum.photos/seed/digitalcny/800/450', source: 'Mock 商业',
      time: h(8), category: 'business', url: '#',
    },
    {
      id: 'mock-b4', title: '楼市回暖信号明确，一线城市成交量环比大涨',
      desc: '住建部最新数据显示，一线城市商品住宅成交面积环比增长35%，二手房挂牌量连续三个月下降。业内认为政策组合拳效果显现，市场信心逐步恢复，但提醒仍需防范炒作风险。',
      image: 'https://picsum.photos/seed/realestate/800/450', source: 'Mock 商业',
      time: h(12), category: 'business', url: '#',
    },
    {
      id: 'mock-b5', title: '即时零售竞争白热化，巨头加码一小时达布局',
      desc: '美团、京东、阿里等电商平台持续加码即时零售业务，将配送时效压缩至30分钟至1小时。2025年即时零售市场规模预计突破8000亿元，生鲜、医药和日用品成为核心品类。',
      image: 'https://picsum.photos/seed/retail/800/450', source: 'Mock 商业',
      time: h(16), category: 'business', url: '#',
    },
    {
      id: 'mock-b6', title: '生物医药融资回暖，创新药研发进入收获期',
      desc: '2025年上半年生物医药领域融资总额同比增长80%，多款国产创新药获FDA批准上市。业内人士指出，在政策支持和资本加持下，中国创新药企正从"跟随创新"向"源头创新"转型。',
      image: 'https://picsum.photos/seed/biotech/800/450', source: 'Mock 商业',
      time: h(20), category: 'business', url: '#',
    },
  ]

  return articles.map(a => ({ ...a, mock: true }))
}

// ============================================
// 4. Application State
// ============================================
const state = {
  articles: [],
  filtered: [],
  loading: true,
  refreshing: false,
  activeCategory: 'all',
  searchQuery: '',
  highlightIndex: -1,
  feedResults: [],
  tickerArticles: [],
  dataSource: 'initializing',
  lastRefresh: null,
  refreshTimer: null,
  countdownTimer: null,
  countdownSeconds: 0,
}

// ============================================
// 5. DOM References
// ============================================
const $ = id => document.getElementById(id)
const dom = {
  grid: $('newsGrid'),
  tickerTrack: $('tickerTrack'),
  articleCount: $('articleCount'),
  statusDot: $('statusDot'),
  updateInfo: $('updateInfo'),
  refreshCountdown: $('refreshCountdown'),
  searchInput: $('searchInput'),
  mobileSearchInput: $('mobileSearchInput'),
  mobileSearchBar: $('mobileSearchBar'),
  mobileSearchBtn: $('mobileSearchBtn'),
  refreshBtn: $('refreshBtn'),
  refreshIcon: $('refreshIcon'),
  themeToggle: $('themeToggle'),
  themeIcon: $('themeIcon'),
  sourceStatus: $('sourceStatus'),
  dataMode: $('dataMode'),
  statsBar: $('statsBar'),
  toastContainer: $('toastContainer'),
  shortcutsModal: $('shortcutsModal'),
  closeShortcuts: $('closeShortcuts'),
  scrollTopBtn: $('scrollTopBtn'),
}

// ============================================
// 6. Utility Functions
// ============================================

/** Strip HTML tags from string */
function stripHtml (html) {
  const d = document.createElement('div')
  d.innerHTML = html
  return d.textContent || d.innerText || ''
}

/** Extract first image URL from RSS item */
function extractImage (item) {
  if (item.enclosure && item.enclosure.link) return item.enclosure.link
  if (item.thumbnail) return item.thumbnail
  const m = item.description && item.description.match(/<img[^>]+src=["']([^"']+)["']/i)
  return m ? m[1] : null
}

/** Format relative time in Chinese */
function formatTime (dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 2592000000) return Math.floor(diff / 86400000) + '天前'
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

/** Debounce utility */
function debounce (fn, ms) {
  let t
  return function (...a) { clearTimeout(t); t = setTimeout(() => fn.apply(this, a), ms) }
}

/** Readable date for stats */
function formatRefreshTime (date) {
  if (!date) return ''
  const d = new Date(date)
  const pad = n => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// ============================================
// 7. Cache (localStorage)
// ============================================
function getCache () {
  try {
    const raw = localStorage.getItem(CONFIG.cacheKey)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (Date.now() - data.ts < CONFIG.cacheTTL) return data.articles
  } catch (_) { /* ignore */ }
  return null
}

function setCache (articles) {
  try {
    localStorage.setItem(CONFIG.cacheKey, JSON.stringify({ ts: Date.now(), articles }))
  } catch (_) { /* ignore */ }
}

// ============================================
// 8. Data Fetching
// ============================================

/** Fetch a single RSS feed via rss2json */
async function fetchFeed (feed) {
  const url = `${CONFIG.rssBase}?rss_url=${encodeURIComponent(feed.url)}`
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), CONFIG.fetchTimeout)

  try {
    const res = await fetch(url, { signal: controller.signal })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    if (json.status !== 'ok') throw new Error(json.message || 'Unknown error')

    const items = (json.items || []).slice(0, 15)
    return items.map((item, i) => ({
      id: `${feed.id}-${i}`,
      title: item.title || '无标题',
      desc: item.description ? stripHtml(item.description).slice(0, 200) : '',
      image: extractImage(item),
      source: feed.name,
      time: item.pubDate ? new Date(item.pubDate).getTime() : Date.now(),
      category: feed.category,
      lang: feed.lang,
      url: item.link || '#',
      feedId: feed.id,
      mock: false,
    }))
  } catch (err) {
    if (err.name === 'AbortError') throw new Error('请求超时')
    throw err
  } finally {
    clearTimeout(timer)
  }
}

/** Fetch all feeds in parallel */
async function fetchAllFeeds () {
  const results = await Promise.allSettled(RSS_FEEDS.map(f => fetchFeed(f)))

  let allArticles = []
  const feedResults = []

  results.forEach((r, i) => {
    const feed = RSS_FEEDS[i]
    if (r.status === 'fulfilled') {
      allArticles = allArticles.concat(r.value)
      feedResults.push({ id: feed.id, name: feed.name, ok: true, count: r.value.length })
    } else {
      feedResults.push({ id: feed.id, name: feed.name, ok: false, error: r.reason.message })
    }
  })

  allArticles.sort((a, b) => b.time - a.time)
  if (allArticles.length > CONFIG.maxArticles) allArticles = allArticles.slice(0, CONFIG.maxArticles)

  return { articles: allArticles, feedResults }
}

/** Load articles: cache -> RSS -> mock */
async function loadArticles () {
  state.loading = true
  updateUI()

  const cached = getCache()
  if (cached && cached.length >= 6) {
    applyArticles(cached, 'cache')
    state.loading = false
    // Refresh in background
    fetchAllFeeds().then(({ articles, feedResults }) => {
      state.feedResults = feedResults
      if (articles.length > 0) {
        setCache(articles)
        applyArticles(articles, 'rss')
      }
    }).catch(() => {})
    return
  }

  try {
    const { articles, feedResults } = await fetchAllFeeds()
    state.feedResults = feedResults
    const hasData = articles.length > 0

    if (hasData) {
      setCache(articles)
      applyArticles(articles, 'rss')
      showToast(`已加载 ${articles.length} 条新闻`, 'success')
    } else {
      // All feeds failed — use mock
      applyArticles(buildMockData(), 'mock')
      showToast('RSS源暂不可用，已切换至离线数据', 'warning')
    }
  } catch (err) {
    applyArticles(buildMockData(), 'mock')
    showToast('网络异常，已切换至离线数据', 'error')
  }

  state.loading = false
}

/** Set articles and re-render */
function applyArticles (articles, source) {
  state.articles = articles
  state.dataSource = source
  state.lastRefresh = Date.now()
  state.highlightIndex = -1
  state.tickerArticles = articles.slice(0, CONFIG.tickerCount)
  applyFilters()
  renderTicker()
  renderSourceStatus()
}

// ============================================
// 9. Filtering & Search
// ============================================

function applyFilters () {
  const { activeCategory, searchQuery, articles } = state
  let filtered = articles

  if (activeCategory !== 'all') {
    filtered = filtered.filter(a => a.category === activeCategory)
  }

  if (searchQuery) {
    const q = searchQuery.toLowerCase()
    filtered = filtered.filter(a =>
      a.title.toLowerCase().includes(q) ||
      a.desc.toLowerCase().includes(q)
    )
  }

  state.filtered = filtered
  renderArticles(filtered)
  updateStats()
}

function handleCategoryChange (cat) {
  if (state.activeCategory === cat) return
  state.activeCategory = cat
  state.highlightIndex = -1

  document.querySelectorAll('.cat-tab').forEach(el => {
    el.classList.toggle('active', el.dataset.cat === cat)
  })

  applyFilters()
  playShortSound()
}

function handleSearch (query) {
  state.searchQuery = query.trim()
  state.highlightIndex = -1
  applyFilters()
}

const debouncedSearch = debounce(handleSearch, 250)

// ============================================
// 10. Rendering — Skeleton
// ============================================

function renderSkeleton () {
  const html = Array.from({ length: 6 }, () => `
    <div class="skeleton-card">
      <div class="skeleton-img"></div>
      <div class="skeleton-body">
        <div class="skeleton-line skeleton-line-sm"></div>
        <div class="skeleton-line skeleton-line-lg"></div>
        <div class="skeleton-line skeleton-line-md"></div>
        <div class="skeleton-line" style="width:45%"></div>
      </div>
    </div>
  `).join('')

  dom.grid.innerHTML = html
}

// ============================================
// 11. Rendering — Article Cards
// ============================================

function createCard (article, index) {
  const card = document.createElement('article')
  card.className = 'news-card anim-card'
  card.dataset.index = index
  if (index === state.highlightIndex) card.classList.add('highlighted')

  // Category badge class
  const badgeClass = `cat-badge cat-badge-${article.category}`

  // Time
  const timeStr = formatTime(article.time)

  // Image or fallback
  let imgHtml
  if (article.image) {
    imgHtml = `<img class="card-img" src="${article.image}" alt="" loading="lazy" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=card-img-fallback><svg width=40 height=40 viewBox=0 0 24 24 fill=none stroke=currentColor stroke-width=1.5><rect x=3 y=3 width=18 height=18 rx=2/><circle cx=8.5 cy=8.5 r=1.5/><path d=M21 15l-5-5L5 21/></svg></div>'">`
  } else {
    imgHtml = `<div class="card-img-fallback"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></div>`
  }

  card.innerHTML = `
    <div class="card-img-wrap">${imgHtml}</div>
    <div class="card-body">
      <div>
        <span class="${badgeClass}">${categoryLabel(article.category)}</span>
        <h3 class="card-title">${article.title}</h3>
      </div>
      <p class="card-desc">${article.desc || '暂无描述'}</p>
      <div class="card-footer">
        <span class="flex items-center gap-1.5">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          ${article.source}
        </span>
        <time class="flex items-center gap-1.5">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          ${timeStr}
        </time>
      </div>
    </div>
  `

  // Click to open URL
  card.addEventListener('click', () => {
    if (article.url && article.url !== '#') {
      window.open(article.url, '_blank', 'noopener')
    }
  })

  return card
}

function categoryLabel (cat) {
  return { tech: '科技', world: '国际', business: '商业' }[cat] || cat
}

function renderArticles (articles) {
  dom.grid.innerHTML = ''

  if (articles.length === 0) {
    dom.grid.innerHTML = `
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="mx-auto mb-4 opacity-50">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
        <p class="text-lg font-medium mb-1">没有找到相关新闻</p>
        <p class="text-sm">试试其他关键词或分类</p>
      </div>
    `
    return
  }

  const fragment = document.createDocumentFragment()
  articles.forEach((article, i) => {
    const card = createCard(article, i)
    fragment.appendChild(card)
  })

  dom.grid.appendChild(fragment)

  // Trigger staggered animation
  requestAnimationFrame(() => {
    const cards = dom.grid.querySelectorAll('.anim-card')
    cards.forEach((card, i) => {
      setTimeout(() => card.classList.add('revealed'), i * CONFIG.animStagger)
    })
  })
}

// ============================================
// 12. Rendering — Ticker
// ============================================

function renderTicker () {
  const items = state.tickerArticles
  if (items.length === 0) {
    dom.tickerTrack.innerHTML = '<span class="ticker-item">暂无头条新闻</span>'
    return
  }

  // Duplicate for seamless loop
  const renderItem = a => `
    <span class="ticker-item" title="${a.title}">
      <span class="ticker-dot"></span>
      <span>${a.title}</span>
    </span>
  `

  dom.tickerTrack.innerHTML = items.map(renderItem).join('') + items.map(renderItem).join('')
}

// ============================================
// 13. Rendering — Source Status & Stats
// ============================================

function renderSourceStatus () {
  const results = state.feedResults
  if (!results || results.length === 0) {
    dom.sourceStatus.innerHTML = `<span style="color:var(--text-muted)">暂无数据源信息</span>`
    return
  }

  dom.sourceStatus.innerHTML = results.map(r => `
    <span class="inline-flex items-center gap-1.5">
      <span class="status-dot ${r.ok ? 'ok' : 'err'}"></span>
      ${r.name}
      <span style="color:var(--text-muted);font-size:0.75em">${r.ok ? r.count + '条' : '×'}</span>
    </span>
  `).join('')

  // Data mode indicator
  const modeMap = { rss: 'RSS在线', cache: '缓存', mock: '离线数据' }
  dom.dataMode.textContent = modeMap[state.dataSource] || '—'
  dom.dataMode.style.borderColor = state.dataSource === 'rss' ? 'var(--accent)' : 'var(--border-color)'
  dom.dataMode.style.color = state.dataSource === 'rss' ? 'var(--accent)' : 'var(--text-muted)'
}

function updateStats () {
  const total = state.articles.length
  const shown = state.filtered.length
  const suffix = total !== shown ? ` (显示 ${shown})` : ''
  dom.articleCount.textContent = `共 ${total} 条新闻${suffix}`

  if (state.lastRefresh) {
    dom.updateInfo.textContent = `更新于 ${formatRefreshTime(state.lastRefresh)}`
  }
}

// ============================================
// 14. Rendering — UI State
// ============================================

function updateUI () {
  if (state.loading) {
    renderSkeleton()
    dom.statusDot.className = 'status-dot pending'
    dom.articleCount.textContent = '加载中…'
  }

  if (state.refreshing) {
    dom.refreshIcon.classList.add('spin-slow')
    dom.refreshBtn.style.pointerEvents = 'none'
  } else {
    dom.refreshIcon.classList.remove('spin-slow')
    dom.refreshBtn.style.pointerEvents = ''
  }
}

// ============================================
// 15. Toast Notifications
// ============================================

function showToast (message, type) {
  const toast = document.createElement('div')
  toast.className = 'toast toast-enter'

  const iconMap = {
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
  }

  toast.innerHTML = (iconMap[type] || '') + `<span>${message}</span>`
  dom.toastContainer.appendChild(toast)

  setTimeout(() => {
    toast.classList.remove('toast-enter')
    toast.classList.add('toast-leave')
    setTimeout(() => toast.remove(), 200)
  }, 3500)
}

// ============================================
// 16. Refresh
// ============================================

async function handleRefresh () {
  if (state.refreshing) return
  state.refreshing = true
  dom.refreshIcon.classList.add('spin-slow')
  dom.refreshBtn.style.pointerEvents = 'none'

  try {
    const { articles, feedResults } = await fetchAllFeeds()
    state.feedResults = feedResults
    if (articles.length > 0) {
      setCache(articles)
      applyArticles(articles, 'rss')
      showToast(`已刷新 — ${articles.length} 条新闻`, 'success')
    } else {
      showToast('未能获取到新内容', 'warning')
    }
  } catch (err) {
    showToast('刷新失败: ' + err.message, 'error')
  }

  state.refreshing = false
  dom.refreshIcon.classList.remove('spin-slow')
  dom.refreshBtn.style.pointerEvents = ''
}

// ============================================
// 17. Auto-Refresh & Countdown
// ============================================

function startAutoRefresh () {
  stopAutoRefresh()
  state.countdownSeconds = Math.floor(CONFIG.refreshInterval / 1000)

  // Countdown tick
  state.countdownTimer = setInterval(() => {
    state.countdownSeconds--
    if (state.countdownSeconds <= 0) state.countdownSeconds = Math.floor(CONFIG.refreshInterval / 1000)
    if (dom.refreshCountdown) {
      const min = Math.floor(state.countdownSeconds / 60)
      const sec = state.countdownSeconds % 60
      dom.refreshCountdown.textContent = `${min}:${String(sec).padStart(2, '0')}`
    }
  }, 1000)

  // Refresh interval
  state.refreshTimer = setInterval(async () => {
    const { articles, feedResults } = await fetchAllFeeds()
    state.feedResults = feedResults
    if (articles.length > 0) {
      setCache(articles)
      applyArticles(articles, 'rss')
    }
  }, CONFIG.refreshInterval)
}

function stopAutoRefresh () {
  if (state.refreshTimer) { clearInterval(state.refreshTimer); state.refreshTimer = null }
  if (state.countdownTimer) { clearInterval(state.countdownTimer); state.countdownTimer = null }
}

// ============================================
// 18. Theme
// ============================================

function toggleTheme () {
  const html = document.documentElement
  const isDark = html.getAttribute('data-theme') !== 'light'
  html.setAttribute('data-theme', isDark ? 'light' : 'dark')
  localStorage.setItem(CONFIG.themeKey, isDark ? 'light' : 'dark')
  dom.themeIcon.setAttribute('data-lucide', isDark ? 'moon' : 'sun')
  lucide.createIcons()
}

function loadTheme () {
  const saved = localStorage.getItem(CONFIG.themeKey)
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved)
    dom.themeIcon.setAttribute('data-lucide', saved === 'dark' ? 'moon' : 'sun')
  }
}

// ============================================
// 19. Keyboard Shortcuts
// ============================================

function setupKeyboardShortcuts () {
  document.addEventListener('keydown', (e) => {
    const tag = document.activeElement && document.activeElement.tagName
    const isInput = tag === 'INPUT' || tag === 'TEXTAREA'

    // ? — help modal
    if (e.key === '?' && !isInput) {
      e.preventDefault()
      dom.shortcutsModal.classList.toggle('hidden')
      return
    }

    // Escape — close modal / blur search
    if (e.key === 'Escape') {
      dom.shortcutsModal.classList.add('hidden')
      if (isInput) document.activeElement.blur()
      return
    }

    // / or s — focus search (even when in input, / doesn't conflict)
    if ((e.key === '/' || (e.key === 's' && !isInput)) && !isInput) {
      e.preventDefault()
      dom.searchInput.focus()
      return
    }

    // Don't process other shortcuts when typing
    if (isInput) return

    switch (e.key.toLowerCase()) {
      case 'r':
        e.preventDefault()
        handleRefresh()
        break
      case 'd':
        e.preventDefault()
        toggleTheme()
        break
      case 'j':
        e.preventDefault()
        navigateHighlight(1)
        break
      case 'k':
        e.preventDefault()
        navigateHighlight(-1)
        break
      case 'enter':
        e.preventDefault()
        openHighlighted()
        break
      case 'g':
        // Double-tap G to go to top
        if (state._gKey) {
          e.preventDefault()
          window.scrollTo({ top: 0, behavior: 'smooth' })
          state._gKey = false
        } else {
          state._gKey = true
          setTimeout(() => { state._gKey = false }, 500)
        }
        break
      case '1': handleCategoryChange('all'); break
      case '2': handleCategoryChange('tech'); break
      case '3': handleCategoryChange('world'); break
      case '4': handleCategoryChange('business'); break
    }
  })
}

function navigateHighlight (dir) {
  const cards = dom.grid.querySelectorAll('.news-card')
  if (cards.length === 0) return

  // Clear current
  cards.forEach(c => c.classList.remove('highlighted'))

  if (state.highlightIndex < 0) {
    state.highlightIndex = dir > 0 ? 0 : cards.length - 1
  } else {
    state.highlightIndex = Math.max(0, Math.min(cards.length - 1, state.highlightIndex + dir))
  }

  cards[state.highlightIndex].classList.add('highlighted')
  cards[state.highlightIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

function openHighlighted () {
  if (state.highlightIndex < 0) return
  const card = dom.grid.querySelector(`.news-card[data-index="${state.highlightIndex}"]`)
  if (card) card.click()
}

function playShortSound () {
  // Subtle haptic via brief CSS class — silent feedback
}

// ============================================
// 20. Show Shortcuts Hint
// ============================================

function showShortcutsHint () {
  const hint = document.createElement('div')
  hint.className = 'toast toast-enter'
  hint.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01"/></svg><span>按 <kbd>?</kbd> 查看键盘快捷键</span>`
  dom.toastContainer.appendChild(hint)
  setTimeout(() => { hint.classList.remove('toast-enter'); hint.classList.add('toast-leave'); setTimeout(() => hint.remove(), 200) }, 4000)
}

// ============================================
// 21. Initialization
// ============================================

function init () {
  // Load theme
  loadTheme()

  // Show skeleton
  renderSkeleton()

  // Load articles
  loadArticles()

  // Setup Lucide
  lucide.createIcons()

  // ---- Event Listeners ----

  // Category clicks (delegated)
  document.querySelectorAll('.cat-tab').forEach(el => {
    el.addEventListener('click', () => handleCategoryChange(el.dataset.cat))
  })

  // Search input
  dom.searchInput.addEventListener('input', e => debouncedSearch(e.target.value))

  // Mobile search
  dom.mobileSearchBtn.addEventListener('click', () => {
    const bar = dom.mobileSearchBar
    bar.classList.toggle('hidden')
    if (!bar.classList.contains('hidden')) {
      dom.mobileSearchInput.focus()
    }
  })
  dom.mobileSearchInput.addEventListener('input', e => debouncedSearch(e.target.value))

  // Refresh
  dom.refreshBtn.addEventListener('click', handleRefresh)

  // Theme
  dom.themeToggle.addEventListener('click', toggleTheme)

  // Scroll to top
  dom.scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })

  // Shortcuts modal
  dom.closeShortcuts.addEventListener('click', () => {
    dom.shortcutsModal.classList.add('hidden')
  })
  dom.shortcutsModal.addEventListener('click', (e) => {
    if (e.target === dom.shortcutsModal) dom.shortcutsModal.classList.add('hidden')
  })

  // Auto-refresh
  startAutoRefresh()

  // Keyboard shortcuts
  setupKeyboardShortcuts()

  // Show hints after short delay
  setTimeout(showShortcutsHint, 2000)

  console.log(`🐚 Hermes News initialized — ${RSS_FEEDS.length} RSS sources, mock fallback ready`)
}

// Start
document.addEventListener('DOMContentLoaded', init)
