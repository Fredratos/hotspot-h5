/**
 * HotSpot Tracker v2.0 - Frontend Application
 * Features: TOP3 multi-platform, real-time news with sources, regional top-20 drill-down
 */

const PLATFORM_CONFIG = {
  weibo: {name:"微博",icon:"📢",color:"#E6162D"},
  bilibili: {name:"B站",icon:"📺",color:"#FB7299"},
  youtube: {name:"YouTube",icon:"▶️",color:"#FF0000"},
  x: {name:"X",icon:"🐦",color:"#1DA1F2"},
  tiktok: {name:"TikTok",icon:"🎬",color:"#000000"},
  instagram: {name:"Instagram",icon:"📷",color:"#E4405F"},
  facebook: {name:"Facebook",icon:"📘",color:"#1877F2"},
  douyin: {name:"抖音",icon:"🎵",color:"#000000"},
};

const REGION_CONFIG = {
  CN:{name:"中国",flag:"🇨🇳"}, HK:{name:"香港",flag:"🇭🇰"},
  JP:{name:"日本",flag:"🇯🇵"}, KR:{name:"韩国",flag:"🇰🇷"},
  TH:{name:"泰国",flag:"🇹🇭"}, IN:{name:"印度",flag:"🇮🇳"},
  SA:{name:"沙特",flag:"🇸🇦"}, BR:{name:"巴西",flag:"🇧🇷"},
  US:{name:"美国",flag:"🇺🇸"}, EU:{name:"欧洲",flag:"🇪🇺"},
  GB:{name:"英国",flag:"🇬🇧"}, RU:{name:"俄罗斯",flag:"🇷🇺"},
};

// API endpoint - auto-detect
const API_BASE = 'http://1.95.104.85:3001';

// ========== BUILT-IN SEED DATA (used when API unavailable) ==========
const SEED_DATA = [
  {title:'2026世界杯亚洲区预选赛中国vs日本',category:'体育',heat_score:9.8,regions:['CN'],first_seen_at:new Date().toISOString(),
    platforms:[{platform:'weibo',platform_rank:1,platform_heat:9.9,discussion_count:520000,interaction_count:1300000,read_count:8900000,source_type:'real'},
      {platform:'x',platform_rank:2,platform_heat:8.5,discussion_count:230000,interaction_count:340000,read_count:4500000,source_type:'real'},
      {platform:'youtube',platform_rank:3,platform_heat:7.8,discussion_count:89000,interaction_count:120000,read_count:2100000,source_type:'real'}]},
  {title:'iPhone 18 Pro真机曝光：全新钛金属设计',category:'科技',heat_score:9.5,regions:['CN','US','EU'],first_seen_at:new Date(Date.now()-3600000).toISOString(),
    platforms:[{platform:'weibo',platform_rank:2,platform_heat:9.2,discussion_count:280000,interaction_count:720000,read_count:5600000,source_type:'real'},
      {platform:'x',platform_rank:1,platform_heat:9.8,discussion_count:450000,interaction_count:1100000,read_count:8900000,source_type:'real'},
      {platform:'youtube',platform_rank:3,platform_heat:8.4,discussion_count:120000,interaction_count:280000,read_count:2300000,source_type:'real'},
      {platform:'instagram',platform_rank:2,platform_heat:8.9,discussion_count:180000,interaction_count:560000,read_count:3400000,source_type:'inferred'}]},
  {title:'Taylor Swift Eras Tour Finale Breaks Attendance Record',category:'娱乐',heat_score:9.9,regions:['US','EU','BR'],first_seen_at:new Date(Date.now()-7200000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.9,discussion_count:890000,interaction_count:2100000,read_count:15000000,source_type:'real'},
      {platform:'instagram',platform_rank:1,platform_heat:9.8,discussion_count:670000,interaction_count:1800000,read_count:12000000,source_type:'inferred'},
      {platform:'tiktok',platform_rank:1,platform_heat:9.7,discussion_count:540000,interaction_count:1500000,read_count:9800000,source_type:'inferred'},
      {platform:'youtube',platform_rank:2,platform_heat:9.0,discussion_count:340000,interaction_count:890000,read_count:6700000,source_type:'real'}]},
  {title:'全球AI监管峰会达成里程碑协议',category:'科技',heat_score:9.3,regions:['US','EU','CN'],first_seen_at:new Date(Date.now()-10800000).toISOString(),
    platforms:[{platform:'x',platform_rank:2,platform_heat:9.2,discussion_count:180000,interaction_count:420000,read_count:3400000,source_type:'real'},
      {platform:'facebook',platform_rank:3,platform_heat:8.7,discussion_count:120000,interaction_count:280000,read_count:2100000,source_type:'inferred'},
      {platform:'youtube',platform_rank:5,platform_heat:8.0,discussion_count:67000,interaction_count:98000,read_count:1200000,source_type:'real'}]},
  {title:'黑神话悟空2首支实机演示发布',category:'游戏',heat_score:9.9,regions:['CN','US','EU'],first_seen_at:new Date(Date.now()-14400000).toISOString(),
    platforms:[{platform:'bilibili',platform_rank:1,platform_heat:9.9,discussion_count:890000,interaction_count:2100000,read_count:12000000,source_type:'real'},
      {platform:'weibo',platform_rank:1,platform_heat:9.8,discussion_count:670000,interaction_count:1600000,read_count:9800000,source_type:'real'},
      {platform:'youtube',platform_rank:4,platform_heat:7.9,discussion_count:110000,interaction_count:280000,read_count:2100000,source_type:'real'},
      {platform:'x',platform_rank:5,platform_heat:7.5,discussion_count:78000,interaction_count:150000,read_count:1200000,source_type:'real'}]},
  {title:'泰国泼水节音乐节吸引全球游客超百万',category:'旅游',heat_score:9.8,regions:['TH'],first_seen_at:new Date(Date.now()-18000000).toISOString(),
    platforms:[{platform:'tiktok',platform_rank:1,platform_heat:9.8,discussion_count:340000,interaction_count:890000,read_count:5600000,source_type:'inferred'},
      {platform:'instagram',platform_rank:2,platform_heat:9.3,discussion_count:210000,interaction_count:560000,read_count:3400000,source_type:'inferred'},
      {platform:'facebook',platform_rank:1,platform_heat:9.5,discussion_count:180000,interaction_count:450000,read_count:2800000,source_type:'inferred'}]},
  {title:'沙特NEOM未来城市一期竣工开放',category:'财经',heat_score:9.6,regions:['SA','US'],first_seen_at:new Date(Date.now()-21600000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.6,discussion_count:280000,interaction_count:670000,read_count:4500000,source_type:'real'},
      {platform:'instagram',platform_rank:3,platform_heat:8.3,discussion_count:89000,interaction_count:210000,read_count:1800000,source_type:'inferred'}]},
  {title:'巴西里约狂欢节创史上最大规模',category:'娱乐',heat_score:9.7,regions:['BR'],first_seen_at:new Date(Date.now()-25200000).toISOString(),
    platforms:[{platform:'instagram',platform_rank:1,platform_heat:9.7,discussion_count:560000,interaction_count:1300000,read_count:8900000,source_type:'inferred'},
      {platform:'tiktok',platform_rank:1,platform_heat:9.5,discussion_count:450000,interaction_count:1100000,read_count:7800000,source_type:'inferred'},
      {platform:'facebook',platform_rank:1,platform_heat:9.3,discussion_count:230000,interaction_count:560000,read_count:3400000,source_type:'inferred'}]},
  {title:'香港Web3金融科技周盛大开幕',category:'财经',heat_score:9.2,regions:['HK'],first_seen_at:new Date(Date.now()-28800000).toISOString(),
    platforms:[{platform:'x',platform_rank:2,platform_heat:8.5,discussion_count:45000,interaction_count:120000,read_count:890000,source_type:'real'},
      {platform:'facebook',platform_rank:3,platform_heat:8.2,discussion_count:34000,interaction_count:89000,read_count:560000,source_type:'inferred'}]},
  {title:'2026欧冠决赛皇马vs曼城巅峰对决',category:'体育',heat_score:9.7,regions:['EU','BR','US'],first_seen_at:new Date(Date.now()-32400000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.7,discussion_count:670000,interaction_count:1800000,read_count:12000000,source_type:'real'},
      {platform:'instagram',platform_rank:2,platform_heat:9.4,discussion_count:450000,interaction_count:1200000,read_count:7800000,source_type:'inferred'},
      {platform:'facebook',platform_rank:2,platform_heat:8.9,discussion_count:280000,interaction_count:670000,read_count:4500000,source_type:'inferred'},
      {platform:'youtube',platform_rank:3,platform_heat:8.2,discussion_count:210000,interaction_count:450000,read_count:3400000,source_type:'real'}]},
  {title:'日本樱花季提前开放吸引全球游客',category:'旅游',heat_score:9.1,regions:['JP'],first_seen_at:new Date(Date.now()-36000000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.1,discussion_count:120000,interaction_count:280000,read_count:2100000,source_type:'real'},
      {platform:'instagram',platform_rank:4,platform_heat:8.6,discussion_count:89000,interaction_count:240000,read_count:1800000,source_type:'inferred'},
      {platform:'tiktok',platform_rank:5,platform_heat:8.0,discussion_count:67000,interaction_count:180000,read_count:1200000,source_type:'inferred'}]},
  {title:'韩国K-Pop全球音乐节仁川盛大举行',category:'娱乐',heat_score:9.4,regions:['KR','JP','TH'],first_seen_at:new Date(Date.now()-39600000).toISOString(),
    platforms:[{platform:'x',platform_rank:2,platform_heat:9.4,discussion_count:340000,interaction_count:890000,read_count:5600000,source_type:'real'},
      {platform:'youtube',platform_rank:1,platform_heat:9.6,discussion_count:280000,interaction_count:720000,read_count:4500000,source_type:'real'},
      {platform:'instagram',platform_rank:1,platform_heat:9.3,discussion_count:450000,interaction_count:1100000,read_count:7800000,source_type:'inferred'},
      {platform:'tiktok',platform_rank:2,platform_heat:9.1,discussion_count:380000,interaction_count:980000,read_count:6700000,source_type:'inferred'}]},
  {title:'印度登月任务Chandrayaan-4成功着陆',category:'科技',heat_score:9.6,regions:['IN','US','EU'],first_seen_at:new Date(Date.now()-43200000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.6,discussion_count:450000,interaction_count:1200000,read_count:8900000,source_type:'real'},
      {platform:'facebook',platform_rank:3,platform_heat:8.4,discussion_count:120000,interaction_count:340000,read_count:2300000,source_type:'inferred'},
      {platform:'youtube',platform_rank:2,platform_heat:8.8,discussion_count:180000,interaction_count:450000,read_count:3400000,source_type:'real'}]},
  {title:'英国皇室婚礼全球直播创纪录',category:'娱乐',heat_score:9.3,regions:['GB','EU','US'],first_seen_at:new Date(Date.now()-46800000).toISOString(),
    platforms:[{platform:'x',platform_rank:1,platform_heat:9.3,discussion_count:560000,interaction_count:1400000,read_count:9800000,source_type:'real'},
      {platform:'instagram',platform_rank:2,platform_heat:9.1,discussion_count:450000,interaction_count:1100000,read_count:7800000,source_type:'inferred'},
      {platform:'facebook',platform_rank:1,platform_heat:8.9,discussion_count:230000,interaction_count:670000,read_count:4500000,source_type:'inferred'}]},
  {title:'俄罗斯胜利日阅兵展示新一代武器装备',category:'军事',heat_score:9.0,regions:['RU','CN'],first_seen_at:new Date(Date.now()-50400000).toISOString(),
    platforms:[{platform:'x',platform_rank:2,platform_heat:8.7,discussion_count:120000,interaction_count:280000,read_count:2100000,source_type:'real'},
      {platform:'youtube',platform_rank:3,platform_heat:8.2,discussion_count:89000,interaction_count:210000,read_count:1800000,source_type:'real'}]},
];

// Add primary_platform to seed data
SEED_DATA.forEach(t => {
  if (!t.primary_platform && t.platforms.length > 0) {
    const best = [...t.platforms].sort((a,b) => b.platform_heat - a.platform_heat)[0];
    t.primary_platform = best.platform;
  }
});

// State
const state = {
  currentTab: 'home',
  currentRegion: 'CN',
  sortBy: 'heat',
  category: '全部',
  followedTopics: new Set(),
  searchHistory: [],
  detailTopicId: null,
  topics: [],       // live data from API
  dataTs: 0,
};

// Utility functions
function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function showToast(msg) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

function formatNum(n) {
  if (n >= 10000) return (n/10000).toFixed(1) + 'w';
  if (n >= 1000) return (n/1000).toFixed(1) + 'k';
  return String(n || 0);
}

function timeAgo(ds) {
  const diff = Date.now() - new Date(ds).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return m + 'm ago';
  const h = Math.floor(m / 60);
  if (h < 24) return h + 'h ago';
  return Math.floor(h / 24) + 'd ago';
}

function platformBadge(p, sourceType) {
  const cfg = PLATFORM_CONFIG[p] || {name:p,icon:'📱'};
  const cls = sourceType === 'inferred' ? 'inferred' : 'real';
  return `<span class="platform-badge ${cls}" title="${cfg.name} (${sourceType==='inferred'?'AI推断':'实时数据'})">
    <span class="dot"></span>${cfg.icon} ${cfg.name}
  </span>`;
}

function sourceTypeLabel(type) {
  return type === 'inferred'
    ? '<span class="data-dot inferred"></span><span style="color:var(--warning);font-size:10px">AI推断</span>'
    : '<span class="data-dot real"></span><span style="color:var(--success);font-size:10px">实时</span>';
}

// ========== DATA FETCHING ==========
async function fetchLiveData() {
  if (!API_BASE) {
    // GitHub Pages mode - use embedded seed data
    return null;
  }
  try {
    const resp = await fetch(`${API_BASE}/api/v1/hotlist`);
    if (!resp.ok) return null;
    const data = await resp.json();
    if (data.topics && data.topics.length > 0) {
      state.topics = data.topics;
      state.dataTs = Date.now();
      return data;
    }
  } catch(e) {
    console.log('[API] fetch error:', e.message);
  }
  return null;
}

function getTopics() {
  if (state.topics.length > 0 && (Date.now() - state.dataTs) < 120000) {
    return state.topics;
  }
  // Fallback to seed data when API unavailable (GitHub Pages mode)
  if (!API_BASE && SEED_DATA.length > 0) {
    return SEED_DATA;
  }
  return [];
}

async function refreshLiveData() {
  const data = await fetchLiveData();
  if (data) {
    if (state.currentTab === 'home') renderHome();
    if (state.currentTab === 'ranking') renderRanking();
  }
}

// ========== RENDER: HOME ==========
function renderHome() {
  const container = $('#screen-home');
  if (!container) return;

  const allTopics = getTopics();
  // TOP 3 globally - sorted by heat_score desc
  const top3 = [...allTopics].sort((a,b) => b.heat_score - a.heat_score).slice(0, 3);
  // Real-time news - latest 10 topics
  const rolling = [...allTopics].sort((a,b) =>
    new Date(b.first_seen_at || 0) - new Date(a.first_seen_at || 0)
  ).slice(0, 10);

  // Region previews
  const regionPreviews = Object.entries(REGION_CONFIG).map(([code, info]) => {
    const inRegion = allTopics.filter(t =>
      (t.regions || []).some(r => r === code)
    ).sort((a,b) => b.heat_score - a.heat_score);
    return {
      code, ...info,
      topicCount: inRegion.length,
      top: inRegion[0] || null
    };
  });

  const now = new Date().toLocaleString('zh-CN');
  const isLive = state.topics.length > 0 && state.dataTs > 0;
  const usingSeed = !API_BASE && SEED_DATA.length > 0;
  const dataStatus = isLive
    ? `<span style="color:var(--success)">● 实时数据 (${state.topics.length}条)</span>`
    : usingSeed
      ? '<span style="color:var(--info)">◉ 演示数据 (部署后端获取实时数据)</span>'
      : '<span style="color:var(--warning)">○ 加载中...</span>';

  container.innerHTML = `
    <div class="update-bar">${dataStatus}<span style="margin-left:auto">${now}</span></div>

    <div class="search-bar" onclick="switchTab('search')">
      <span class="icon">🔍</span>
      <span class="placeholder">搜索全球热点话题...</span>
    </div>

    <div class="section-title">🔥 今日最热 TOP 3<span class="count">跨平台综合热度</span></div>
    ${top3.length > 0 ? top3.map((t, i) => `
      <div class="topic-card rank-${i+1}" onclick="showDetail(${t.title.replace(/'/g,"\\'")})">
        <div class="rank-badge">#${i+1}</div>
        <div class="topic-title">${escHtml(t.title)}</div>
        <div class="flex-row gap-8" style="margin-top:8px">
          <span class="heat-score">🔥 ${t.heat_score}</span>
          <span class="tag tag-primary">${t.category || '其他'}</span>
        </div>
        <div class="platform-row">
          ${(t.platforms || []).slice(0, 6).map(p => platformBadge(p.platform, p.source_type)).join('')}
        </div>
        <div class="data-source" style="margin-top:4px">
          <span class="data-dot real"></span> 多平台实时聚合 · ${(t.platforms || []).length}个平台
        </div>
      </div>
    `).join('') : `
      <div class="card" style="text-align:center;padding:30px">
        <div style="font-size:32px;margin-bottom:8px">⏳</div>
        <div style="color:var(--text-muted)">正在获取实时数据...</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">多平台数据聚合需要约1分钟</div>
      </div>
    `}

    <div class="section-title">📡 实时快讯 TOP 10<span class="count">最新上榜话题</span></div>
    <div style="background:var(--bg-card);border-radius:12px;padding:4px 12px;border:1px solid var(--border)">
      ${rolling.length > 0 ? rolling.map((t, i) => `
        <div class="rolling-news-item" onclick="showTopicByTitle('${escHtml(t.title).replace(/'/g,"\\'")}')">
          <span class="rn-rank">${i+1}</span>
          <span class="rn-title">${escHtml(t.title)}</span>
          <span class="rn-source">${(PLATFORM_CONFIG[t.primary_platform] || {}).icon || '📱'} ${PLATFORM_CONFIG[t.primary_platform]?.name || t.primary_platform || ''}</span>
        </div>
      `).join('') : '<div style="padding:16px;text-align:center;color:var(--text-muted)">等待实时数据...</div>'}
    </div>

    <div class="section-title">🌍 区域热点一览<span class="count">点击查看TOP 20</span></div>
    <div class="region-grid">
      ${regionPreviews.map(r => `
        <div class="region-preview" onclick="switchToRegion('${r.code}')">
          <div class="flag">${r.flag} ${r.name}</div>
          ${r.top ? `
            <div class="topic-text">${escHtml(r.top.title)}</div>
            <div class="text-sm text-muted">🔥 ${r.top.heat_score} · ${r.topicCount}条话题</div>
          ` : '<div class="text-sm text-muted">暂无数据</div>'}
        </div>
      `).join('')}
    </div>
  `;
}

function switchToRegion(code) {
  state.currentRegion = code;
  state.sortBy = 'heat';
  state.category = '全部';
  switchTab('ranking');
}

// ========== RENDER: RANKING (Regional TOP 20) ==========
function renderRanking() {
  const container = $('#screen-ranking');
  if (!container) return;

  const sortOptions = [
    {key:'heat', label:'综合热度'},
    {key:'time', label:'最新上榜'},
    {key:'platforms', label:'覆盖平台数'}
  ];
  const categories = ['全部','娱乐','科技','体育','游戏','财经','社会','教育','旅游','军事','国际','其他'];

  const regionInfo = REGION_CONFIG[state.currentRegion] || {name: state.currentRegion, flag: '🌐'};
  let topics = [...getTopics()];

  // Filter by region
  topics = topics.filter(t => (t.regions || []).some(r => r === state.currentRegion));

  // Category filter
  if (state.category !== '全部') {
    topics = topics.filter(t => t.category === state.category);
  }

  // Sort
  switch(state.sortBy) {
    case 'heat':
      topics.sort((a,b) => b.heat_score - a.heat_score);
      break;
    case 'time':
      topics.sort((a,b) => new Date(b.first_seen_at||0) - new Date(a.first_seen_at||0));
      break;
    case 'platforms':
      topics.sort((a,b) => (b.platforms||[]).length - (a.platforms||[]).length);
      break;
  }

  const top20 = topics.slice(0, 20);

  container.innerHTML = `
    <div class="region-tabs">
      ${Object.entries(REGION_CONFIG).map(([code, info]) => `
        <div class="region-tab ${code === state.currentRegion ? 'active' : ''}" onclick="setRegion('${code}')">
          ${info.flag} ${info.name}
        </div>
      `).join('')}
    </div>
    <div class="filter-bar">
      ${sortOptions.map(s => `
        <div class="filter-btn ${s.key === state.sortBy ? 'active' : ''}" onclick="setSort('${s.key}')">${s.label}</div>
      `).join('')}
      <select onchange="setCategory(this.value)" style="margin-left:auto;padding:8px 12px;border-radius:8px;background:var(--bg-card);color:var(--text);border:1px solid var(--border);font-size:13px">
        ${categories.map(c => `<option value="${c}" ${c === state.category ? 'selected' : ''}>${c}</option>`).join('')}
      </select>
    </div>
    <div class="flex-between" style="margin-bottom:8px">
      <span class="text-sm text-muted">📋 ${regionInfo.flag} ${regionInfo.name} TOP ${top20.length}</span>
      <span class="text-sm text-muted">${new Date().toLocaleDateString('zh-CN')}</span>
    </div>
    ${top20.length > 0 ? top20.map((t, i) => `
      <div class="topic-list-item ${i < 3 ? 'top-rank' : ''}" onclick="showTopicByTitle('${escHtml(t.title).replace(/'/g,"\\'")}')">
        <div class="rank-num">${i+1}</div>
        <div class="list-body">
          <div class="list-title">${escHtml(t.title)}</div>
          <div class="flex-row gap-8" style="margin-top:4px">
            <span class="heat-score">🔥 ${t.heat_score}</span>
            <span class="tag tag-primary">${t.category || '其他'}</span>
          </div>
          <div class="platform-row">
            ${(t.platforms || []).slice(0, 4).map(p => platformBadge(p.platform, p.source_type)).join('')}
          </div>
          <div class="data-source">
            ${sourceTypeLabel((t.platforms||[])[0]?.source_type)} · ${(t.platforms||[]).length}个平台覆盖
          </div>
        </div>
      </div>
    `).join('') : `<div class="empty"><div class="icon">📭</div><div>该区域暂无热点数据</div></div>`}
  `;
}

function setRegion(code) { state.currentRegion = code; renderRanking(); }
function setSort(sort) { state.sortBy = sort; renderRanking(); }
function setCategory(cat) { state.category = cat; renderRanking(); }

// ========== RENDER: DETAIL ==========
let currentDetailTopic = null;

function showTopicByTitle(title) {
  const t = getTopics().find(t => t.title === title);
  if (t) {
    currentDetailTopic = t;
    renderDetail();
    showScreen('detail');
    renderDetailActionBar();
    window.scrollTo(0, 0);
  }
}

function showDetail(title) {
  // title is passed from onclick, we need to find the topic
  const escaped = title; // already escaped
  const t = getTopics().find(t => t.title === title);
  if (!t) {
    // Try unescape
    const txt = document.createElement('textarea');
    txt.innerHTML = title;
    const decoded = txt.value;
    const t2 = getTopics().find(t => t.title === decoded);
    if (t2) {
      currentDetailTopic = t2;
    } else {
      return;
    }
  } else {
    currentDetailTopic = t;
  }
  renderDetail();
  showScreen('detail');
  renderDetailActionBar();
  window.scrollTo(0, 0);
}

function renderDetail() {
  const container = $('#screen-detail');
  if (!container || !currentDetailTopic) {
    if (container) container.innerHTML = '<div class="empty">话题不存在</div>';
    return;
  }

  const t = currentDetailTopic;
  const platforms = t.platforms || [];

  container.innerHTML = `
    <div class="back-btn" onclick="showScreen('home')">← 返回</div>
    <div class="detail-title">${escHtml(t.title)}</div>
    <div class="flex-row gap-16" style="margin-bottom:16px;flex-wrap:wrap">
      <span class="heat-big">🔥 ${t.heat_score}</span>
      <span class="tag tag-primary">${t.category || '其他'}</span>
    </div>
    <div class="text-sm text-muted" style="margin-bottom:20px">首次上榜：${timeAgo(t.first_seen_at)}</div>

    <div class="card">
      <div style="font-weight:600;margin-bottom:12px">🔗 跨平台溯源 (${platforms.length}个平台)</div>
      ${platforms.length > 0 ? platforms.map(p => `
        <div class="platform-trace-item">
          <div class="platform-icon">${(PLATFORM_CONFIG[p.platform] || {}).icon || '📱'}</div>
          <div class="platform-trace-info">
            <div class="trace-rank">${(PLATFORM_CONFIG[p.platform] || {}).name || p.platform} · 排名 #${p.platform_rank || '-'}</div>
            <div class="text-sm">${sourceTypeLabel(p.source_type)} · 热度 ${p.platform_heat || '-'}</div>
          </div>
          <div class="text-sm text-muted" style="text-align:right">
            ${p.discussion_count ? '讨论 '+formatNum(p.discussion_count) : ''}
            ${p.interaction_count ? '<br>互动 '+formatNum(p.interaction_count) : ''}
            ${p.read_count ? '<br>阅读 '+formatNum(p.read_count) : ''}
          </div>
        </div>
      `).join('') : '<div class="text-sm text-muted" style="padding:10px 0">暂无平台数据</div>'}
    </div>

    <div class="card">
      <div style="font-weight:600;margin-bottom:8px">🌍 覆盖区域</div>
      <div class="flex-row flex-wrap gap-8">
        ${(t.regions || ['CN']).map(r => {
          const info = REGION_CONFIG[r];
          return `<span class="tag tag-info">${info ? info.flag+' '+info.name : r}</span>`;
        }).join('')}
      </div>
    </div>

    <div style="height:100px"></div>
  `;
}

function renderDetailActionBar() {
  let bar = $('#detailActionBar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'detailActionBar';
    bar.className = 'action-bar';
    $('#app').appendChild(bar);
  }
  const title = currentDetailTopic?.title || '';
  const isFollowed = state.followedTopics.has(title);
  bar.innerHTML = `
    <button class="btn-primary" onclick="toggleFollowDetail('${escHtml(title).replace(/'/g,"\\'")}')">${isFollowed ? '✓ 已关注' : '⭐ 关注'}</button>
    <button class="btn-secondary" onclick="shareTopic()">🔗 分享</button>
  `;
  bar.style.display = 'flex';
}

function toggleFollowDetail(title) {
  if (state.followedTopics.has(title)) {
    state.followedTopics.delete(title);
    showToast('已取消关注');
  } else {
    state.followedTopics.add(title);
    showToast('关注成功');
  }
  renderDetailActionBar();
}

function shareTopic() {
  const t = currentDetailTopic;
  const text = `🔥 ${t?.title || '热点话题'}\n综合热度: ${t?.heat_score || '-'}\n来源: HotSpot Tracker 全球热点追踪`;
  if (navigator.share) {
    navigator.share({title: `🔥 ${t?.title || '热点'}`, text, url: window.location.href}).catch(() => {});
  } else {
    navigator.clipboard.writeText(text).then(() => showToast('已复制分享文本')).catch(() => showToast('分享暂不可用'));
  }
}

// ========== RENDER: SEARCH ==========
function renderSearch() {
  const container = $('#screen-search');
  if (!container) return;

  const topics = getTopics();
  const hotKeywords = [...new Set(topics.map(t => t.title.split(/[\s，。！]/)[0]))].slice(0, 10);

  container.innerHTML = `
    <div class="search-input-wrap">
      <div class="search-input">
        <span style="margin-right:8px;font-size:18px">🔍</span>
        <input type="text" id="searchInput" placeholder="搜索全球热点话题..." onkeyup="handleSearchKeyup(event)">
      </div>
      <span class="cancel-btn" onclick="clearSearch()">取消</span>
    </div>
    <div id="searchResults"></div>
    <div id="searchDefault">
      <div style="font-weight:600;margin:20px 0 12px;color:#fff">🔥 热门搜索</div>
      <div class="keyword-cloud">
        ${hotKeywords.map(k => `
          <span class="keyword-tag" onclick="quickSearch('${escHtml(k).replace(/'/g,"\\'")}')">${escHtml(k)}</span>
        `).join('')}
      </div>
    </div>
  `;
}

function handleSearchKeyup(e) {
  if (e.key === 'Enter') performSearch(e.target.value);
}
function quickSearch(keyword) {
  const input = $('#searchInput');
  if (input) { input.value = keyword; }
  performSearch(keyword);
}
function performSearch(q) {
  const resultsDiv = $('#searchResults');
  const defaultDiv = $('#searchDefault');
  if (!q || !q.trim()) {
    if (defaultDiv) defaultDiv.style.display = 'block';
    if (resultsDiv) resultsDiv.innerHTML = '';
    return;
  }
  if (defaultDiv) defaultDiv.style.display = 'none';

  const query = q.trim().toLowerCase();
  const results = getTopics().filter(t =>
    t.title.toLowerCase().includes(query) ||
    (t.category || '').toLowerCase().includes(query)
  );

  if (resultsDiv) {
    resultsDiv.innerHTML = results.length > 0 ? `
      <div class="text-sm text-muted" style="margin-bottom:12px">找到 ${results.length} 个相关话题</div>
      ${results.map(t => `
        <div class="search-result-item" onclick="showTopicByTitle('${escHtml(t.title).replace(/'/g,"\\'")}')">
          <div class="result-title">${escHtml(t.title)}</div>
          <div class="flex-row gap-8" style="margin-top:6px">
            <span class="heat-score">🔥 ${t.heat_score}</span>
            <span class="tag tag-primary">${t.category || '其他'}</span>
          </div>
          <div class="platform-row">${(t.platforms||[]).slice(0,3).map(p => platformBadge(p.platform, p.source_type)).join('')}</div>
        </div>
      `).join('')}
    ` : `<div class="empty"><div class="icon">🔍</div><div>未找到相关话题</div></div>`;
  }
}
function clearSearch() {
  const input = $('#searchInput');
  if (input) input.value = '';
  const r = $('#searchResults'); if (r) r.innerHTML = '';
  const d = $('#searchDefault'); if (d) d.style.display = 'block';
}

// ========== RENDER: MINE ==========
function renderMine() {
  const container = $('#screen-mine');
  if (!container) return;

  const followedTopics = getTopics().filter(t => state.followedTopics.has(t.title));

  container.innerHTML = `
    <div class="card user-card">
      <div class="avatar">👤</div>
      <div>
        <div class="nickname">热点追踪用户</div>
        <div class="text-sm text-muted">关注话题 · 浏览历史</div>
      </div>
    </div>
    <div class="card">
      <div style="font-weight:600;margin-bottom:12px">⭐ 我的关注</div>
      ${followedTopics.length > 0 ? followedTopics.map(t => `
        <div style="padding:12px 0;border-bottom:1px solid rgba(51,65,85,0.5);cursor:pointer" onclick="showTopicByTitle('${escHtml(t.title).replace(/'/g,"\\'")}')">
          <div style="font-size:15px;font-weight:500;color:#fff;margin-bottom:6px">${escHtml(t.title)}</div>
          <div class="flex-row gap-8">
            <span class="heat-score">🔥 ${t.heat_score}</span>
            <span class="tag tag-primary">${t.category || '其他'}</span>
          </div>
        </div>
      `).join('') : `<div class="empty" style="padding:20px"><div class="icon">📭</div><div>还没有关注话题</div><div class="text-sm text-muted">在话题详情页点击关注即可追踪</div></div>`}
    </div>
    <div class="card">
      <div class="menu-item" onclick="switchTab('search')"><span>🔍 搜索话题</span><span class="text-muted">›</span></div>
    </div>
    <div class="card" style="text-align:center;padding:24px">
      <div style="font-size:20px;font-weight:700;color:var(--primary);margin-bottom:8px">🔥 HotSpot Tracker</div>
      <div class="text-sm text-muted">v2.0 · 全球社交媒体热点聚合</div>
      <div class="text-sm text-muted">数据源：微博 · B站 · YouTube · X · Facebook · Instagram · TikTok</div>
      <div style="margin-top:8px;font-size:11px;color:var(--text-muted)">
        ${state.topics.length > 0 ? `实时数据 · ${state.topics.length}条话题` : '离线模式'}
      </div>
    </div>
  `;
}

// ========== SCREEN NAVIGATION ==========
function showScreen(name) {
  $$('.screen').forEach(s => s.classList.remove('active'));
  const screen = $(`#screen-${name}`);
  if (screen) screen.classList.add('active');

  const detailBar = $('#detailActionBar');
  if (detailBar) {
    detailBar.style.display = name === 'detail' ? 'flex' : 'none';
  }
}

// ========== TAB SWITCHING ==========
function switchTab(tab) {
  state.currentTab = tab;
  showScreen(tab);
  $$('.tab-item').forEach(b => b.classList.remove('active'));
  const tabBtn = $(`.tab-item[data-tab="${tab}"]`);
  if (tabBtn) tabBtn.classList.add('active');

  switch(tab) {
    case 'home': renderHome(); break;
    case 'ranking': renderRanking(); break;
    case 'search': renderSearch(); break;
    case 'mine': renderMine(); break;
  }
}

// ========== HTML ESCAPE ==========
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ========== INITIALIZATION ==========
function init() {
  const app = $('#app');
  if (!app) return;

  // Create all screens
  ['home', 'ranking', 'search', 'mine', 'detail'].forEach(name => {
    const screen = document.createElement('div');
    screen.id = `screen-${name}`;
    screen.className = `screen ${name === 'home' ? 'active' : ''}`;
    app.appendChild(screen);
  });

  // Tab bar handlers
  $$('.tab-item').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Initial render
  renderHome();
  renderRanking();
  renderSearch();

  // Start periodic refresh
  fetchLiveData().then(data => {
    if (data && state.currentTab === 'home') renderHome();
  });

  // Periodic refresh every  mins
  setInterval(async () => {
    await refreshLiveData();
  }, 60000);
}

document.addEventListener('DOMContentLoaded', init);

// Expose global functions for onclick handlers
window.switchTab = switchTab;
window.showScreen = showScreen;
window.showTopicByTitle = showTopicByTitle;
window.showDetail = showDetail;
window.setRegion = setRegion;
window.setSort = setSort;
window.setCategory = setCategory;
window.switchToRegion = switchToRegion;
window.toggleFollowDetail = toggleFollowDetail;
window.shareTopic = shareTopic;
window.handleSearchKeyup = handleSearchKeyup;
window.quickSearch = quickSearch;
window.clearSearch = clearSearch;
