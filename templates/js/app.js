const API_BASE = '/api';

let videos = [];
let mergeQueue = [];
let jobs = [];
let tiktokDownloads = [];

document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initNavigation();
    initUpload();
    initSplit();
    initMerge();
    initTikTok();
    
    await cleanupOnLoad();
    
    loadVideos();
    loadStats();
    pollJobs();
});

async function cleanupOnLoad() {
    try {
        await fetch(`${API_BASE}/cleanup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        console.log('Cleanup completed on page load');
    } catch (err) {
        console.error('Cleanup error:', err);
    }
}

function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        html.classList.remove('dark');
    } else if (savedTheme === 'dark') {
        html.classList.add('dark');
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const isDark = html.classList.contains('dark');
            if (isDark) {
                html.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            } else {
                html.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
}

function initNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            navigateToPage(btn.dataset.page);
        });
    });
    
    document.querySelectorAll('.service-block').forEach(block => {
        block.addEventListener('click', () => {
            navigateToPage(block.dataset.goto);
        });
    });
}

function navigateToPage(pageName) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => {
        p.classList.add('hidden');
        p.classList.remove('active');
    });
    
    const navBtn = document.querySelector(`.nav-btn[data-page="${pageName}"]`);
    if (navBtn) navBtn.classList.add('active');
    
    const page = document.getElementById(`page-${pageName}`);
    if (page) {
        page.classList.remove('hidden');
        page.classList.add('active');
    }
    
    if (pageName === 'split') updateSplitVideoSelect();
    if (pageName === 'stats') loadStats();
}


function initUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('video-input');
    
    zone.addEventListener('click', () => input.click());
    
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });
    
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadVideo(files[0]);
    });
    
    input.addEventListener('change', () => {
        if (input.files.length > 0) uploadVideo(input.files[0]);
    });
}

async function uploadVideo(file) {
    const progressDiv = document.getElementById('upload-progress');
    const filenameEl = document.getElementById('upload-filename');
    const percentEl = document.getElementById('upload-percent');
    const barEl = document.getElementById('upload-bar');
    
    progressDiv.classList.remove('hidden');
    filenameEl.textContent = file.name;
    
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                percentEl.textContent = percent + '%';
                barEl.style.width = percent + '%';
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                setTimeout(() => {
                    progressDiv.classList.add('hidden');
                    barEl.style.width = '0%';
                    loadVideos();
                }, 500);
            } else {
                alert('Erreur lors de l\'upload');
                progressDiv.classList.add('hidden');
            }
        });
        
        xhr.addEventListener('error', () => {
            alert('Erreur réseau');
            progressDiv.classList.add('hidden');
        });
        
        xhr.open('POST', `${API_BASE}/videos/upload`);
        xhr.send(formData);
    } catch (err) {
        console.error('Upload error:', err);
        alert('Erreur lors de l\'upload');
        progressDiv.classList.add('hidden');
    }
}

async function loadVideos() {
    try {
        const res = await fetch(`${API_BASE}/videos`);
        videos = await res.json();
        renderVideos();
        updateSplitVideoSelect();
    } catch (err) {
        console.error('Error loading videos:', err);
    }
}

function renderVideos() {
    const container = document.getElementById('videos-container');
    
    if (videos.length === 0) {
        container.innerHTML = `
            <div class="text-center text-night-500 dark:text-night-400 py-8">
                <p>Aucune vidéo uploadée</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = videos.map(v => `
        <div class="video-card" data-testid="video-card-${v.id}">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="font-medium truncate text-night-900 dark:text-white">${v.originalName}</p>
                    <div class="flex items-center gap-3 text-xs text-night-500 dark:text-night-400">
                        <span>${formatDuration(v.duration)}</span>
                        <span>${formatFileSize(v.size)}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function initSplit() {
    const select = document.getElementById('split-video-select');
    const durationInput = document.getElementById('segment-duration');
    const btnSplit = document.getElementById('btn-split');
    const splitUploadZone = document.getElementById('split-upload-zone');
    const splitVideoInput = document.getElementById('split-video-input');
    
    splitUploadZone.addEventListener('click', () => splitVideoInput.click());
    
    splitUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        splitUploadZone.classList.add('dragover');
    });
    
    splitUploadZone.addEventListener('dragleave', () => {
        splitUploadZone.classList.remove('dragover');
    });
    
    splitUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        splitUploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadVideoForSplit(e.dataTransfer.files[0]);
        }
    });
    
    splitVideoInput.addEventListener('change', () => {
        if (splitVideoInput.files.length > 0) {
            uploadVideoForSplit(splitVideoInput.files[0]);
        }
    });
    
    select.addEventListener('change', updateSplitPreview);
    durationInput.addEventListener('input', updateSplitPreview);
    
    btnSplit.addEventListener('click', () => {
        const videoId = select.value;
        const segmentDuration = parseInt(durationInput.value);
        
        if (videoId && segmentDuration > 0) {
            splitVideo(videoId, segmentDuration);
        }
    });
}

async function uploadVideoForSplit(file) {
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        const res = await fetch(`${API_BASE}/videos/upload`, {
            method: 'POST',
            body: formData
        });
        
        const video = await res.json();
        if (video.id) {
            videos.push(video);
            updateSplitVideoSelect();
            document.getElementById('split-video-select').value = video.id;
            updateSplitPreview();
        }
    } catch (err) {
        console.error('Error uploading video for split:', err);
        alert('Erreur lors de l\'upload');
    }
}

function updateSplitVideoSelect() {
    const select = document.getElementById('split-video-select');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">Choisir une vidéo...</option>' + 
        videos.map(v => `<option value="${v.id}">${v.originalName} (${formatDuration(v.duration)})</option>`).join('');
    
    if (currentValue && videos.find(v => v.id === currentValue)) {
        select.value = currentValue;
    }
    
    updateSplitPreview();
}

function updateSplitPreview() {
    const select = document.getElementById('split-video-select');
    const durationInput = document.getElementById('segment-duration');
    const infoDiv = document.getElementById('split-video-info');
    const previewDiv = document.getElementById('split-preview');
    const btnSplit = document.getElementById('btn-split');
    const durationEl = document.getElementById('split-duration');
    const countEl = document.getElementById('segment-count');
    const boxesEl = document.getElementById('segment-preview-boxes');
    
    const video = videos.find(v => v.id === select.value);
    const segmentDuration = parseInt(durationInput.value) || 0;
    
    if (!video || segmentDuration <= 0) {
        infoDiv.classList.add('hidden');
        previewDiv.classList.add('hidden');
        btnSplit.disabled = true;
        return;
    }
    
    infoDiv.classList.remove('hidden');
    previewDiv.classList.remove('hidden');
    btnSplit.disabled = false;
    
    durationEl.textContent = formatDuration(video.duration);
    
    const segmentCount = Math.ceil(video.duration / segmentDuration);
    countEl.textContent = segmentCount;
    
    const boxes = [];
    for (let i = 0; i < Math.min(segmentCount, 20); i++) {
        boxes.push(`<div class="segment-box">${i + 1}</div>`);
    }
    if (segmentCount > 20) {
        boxes.push(`<div class="segment-box">...</div>`);
    }
    boxesEl.innerHTML = boxes.join('');
}

async function splitVideo(videoId, segmentDuration) {
    const btnSplit = document.getElementById('btn-split');
    const originalContent = btnSplit.innerHTML;
    btnSplit.disabled = true;
    btnSplit.innerHTML = `<span class="flex items-center justify-center gap-2">
        <div class="w-6 h-6"><dotlottie-player src="https://lottie.host/fe611542-3d6e-4a7a-939b-f057ee86c662/mHagjNySSC.lottie" background="transparent" speed="1" style="width:24px;height:24px" loop autoplay></dotlottie-player></div>
        Traitement...
    </span>`;
    
    try {
        const res = await fetch(`${API_BASE}/videos/split`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ videoId, segmentDuration })
        });
        
        const data = await res.json();
        
        if (data.jobId) {
            pollJobs();
        }
    } catch (err) {
        console.error('Split error:', err);
        alert('Erreur lors de la découpe');
    } finally {
        btnSplit.disabled = false;
        btnSplit.innerHTML = originalContent;
    }
}

function initMerge() {
    const zone = document.getElementById('merge-upload-zone');
    const input = document.getElementById('merge-video-input');
    const btnMerge = document.getElementById('btn-merge');
    
    zone.addEventListener('click', () => input.click());
    
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });
    
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleMergeFiles(e.dataTransfer.files);
    });
    
    input.addEventListener('change', () => {
        handleMergeFiles(input.files);
    });
    
    btnMerge.addEventListener('click', mergeVideos);
}

async function handleMergeFiles(files) {
    for (const file of files) {
        const formData = new FormData();
        formData.append('video', file);
        
        try {
            const res = await fetch(`${API_BASE}/videos/upload`, {
                method: 'POST',
                body: formData
            });
            
            const video = await res.json();
            mergeQueue.push(video);
            renderMergeQueue();
        } catch (err) {
            console.error('Error uploading for merge:', err);
        }
    }
}

function renderMergeQueue() {
    const container = document.getElementById('merge-queue');
    const infoDiv = document.getElementById('merge-info');
    const countEl = document.getElementById('merge-count');
    const durationEl = document.getElementById('merge-total-duration');
    const btnMerge = document.getElementById('btn-merge');
    
    if (mergeQueue.length === 0) {
        container.innerHTML = '';
        infoDiv.classList.add('hidden');
        btnMerge.disabled = true;
        return;
    }
    
    infoDiv.classList.remove('hidden');
    btnMerge.disabled = mergeQueue.length < 2;
    
    countEl.textContent = mergeQueue.length;
    const totalDuration = mergeQueue.reduce((sum, v) => sum + v.duration, 0);
    durationEl.textContent = formatDuration(totalDuration);
    
    container.innerHTML = mergeQueue.map((v, i) => `
        <div class="merge-item" data-testid="merge-item-${i}">
            <div class="flex items-center gap-2 flex-1 min-w-0">
                <span class="w-6 h-6 bg-success/20 rounded-full flex items-center justify-center text-xs font-bold">${i + 1}</span>
                <span class="truncate text-sm">${v.originalName}</span>
            </div>
            <button onclick="removeMergeItem(${i})" class="text-red-400 hover:text-red-300 p-1" data-testid="button-remove-merge-${i}">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        </div>
    `).join('');
}

function removeMergeItem(index) {
    mergeQueue.splice(index, 1);
    renderMergeQueue();
}

async function mergeVideos() {
    if (mergeQueue.length < 2) return;
    
    const btnMerge = document.getElementById('btn-merge');
    const originalContent = btnMerge.innerHTML;
    btnMerge.disabled = true;
    btnMerge.innerHTML = `<span class="flex items-center justify-center gap-2">
        <div class="w-6 h-6"><dotlottie-player src="https://lottie.host/fe611542-3d6e-4a7a-939b-f057ee86c662/mHagjNySSC.lottie" background="transparent" speed="1" style="width:24px;height:24px" loop autoplay></dotlottie-player></div>
        Fusion...
    </span>`;
    
    try {
        const res = await fetch(`${API_BASE}/videos/merge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ videoIds: mergeQueue.map(v => v.id) })
        });
        
        const data = await res.json();
        
        if (data.jobId) {
            mergeQueue = [];
            renderMergeQueue();
            pollJobs();
        }
    } catch (err) {
        console.error('Merge error:', err);
        alert('Erreur lors de la fusion');
    } finally {
        btnMerge.disabled = mergeQueue.length < 2;
        btnMerge.innerHTML = originalContent;
    }
}

function initTikTok() {
    const urlInput = document.getElementById('tiktok-url');
    const btnDownload = document.getElementById('btn-tiktok-download');
    
    btnDownload.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (url) {
            downloadTikTok(url);
        }
    });
    
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const url = urlInput.value.trim();
            if (url) {
                downloadTikTok(url);
            }
        }
    });
}

async function downloadTikTok(url) {
    const btnDownload = document.getElementById('btn-tiktok-download');
    const loadingDiv = document.getElementById('tiktok-loading');
    const urlInput = document.getElementById('tiktok-url');
    const originalContent = btnDownload.innerHTML;
    
    btnDownload.disabled = true;
    btnDownload.innerHTML = `<span class="flex items-center justify-center gap-2">
        <div class="w-6 h-6"><dotlottie-player src="https://lottie.host/fe611542-3d6e-4a7a-939b-f057ee86c662/mHagjNySSC.lottie" background="transparent" speed="1" style="width:24px;height:24px" loop autoplay></dotlottie-player></div>
        Téléchargement...
    </span>`;
    loadingDiv.classList.remove('hidden');
    
    try {
        const res = await fetch(`${API_BASE}/social/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await res.json();
        
        if (data.error) {
            alert(data.error);
        } else {
            tiktokDownloads.unshift(data);
            renderTikTokDownloads();
            urlInput.value = '';
        }
    } catch (err) {
        console.error('Social download error:', err);
        alert('Erreur lors du téléchargement');
    } finally {
        btnDownload.disabled = false;
        btnDownload.innerHTML = originalContent;
        loadingDiv.classList.add('hidden');
    }
}

function renderTikTokDownloads() {
    const container = document.getElementById('tiktok-downloads-container');
    
    if (tiktokDownloads.length === 0) {
        container.innerHTML = `
            <div class="text-center text-night-500 dark:text-night-400 py-8">
                <p>Aucune vidéo téléchargée</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tiktokDownloads.map(v => {
        let iconBgClass = 'bg-purple-500/20';
        let iconTextClass = 'text-purple-500';
        let badgeBgClass = 'bg-purple-500/20';
        let badgeTextClass = 'text-purple-500';
        
        if (v.platform === 'TikTok') {
            iconBgClass = 'bg-tiktok/20';
            iconTextClass = 'text-tiktok';
            badgeBgClass = 'bg-tiktok/20';
            badgeTextClass = 'text-tiktok';
        } else if (v.platform === 'Instagram') {
            iconBgClass = 'bg-pink-500/20';
            iconTextClass = 'text-pink-500';
            badgeBgClass = 'bg-pink-500/20';
            badgeTextClass = 'text-pink-500';
        } else if (v.platform === 'Facebook') {
            iconBgClass = 'bg-blue-600/20';
            iconTextClass = 'text-blue-600';
            badgeBgClass = 'bg-blue-600/20';
            badgeTextClass = 'text-blue-600';
        } else if (v.platform === 'YouTube') {
            iconBgClass = 'bg-red-600/20';
            iconTextClass = 'text-red-600';
            badgeBgClass = 'bg-red-600/20';
            badgeTextClass = 'text-red-600';
        }
        
        return `
        <div class="social-download-card bg-white/80 dark:bg-night-800/50 backdrop-blur-lg rounded-xl p-4 border border-night-200 dark:border-night-700 mb-3" data-testid="social-card-${v.id}">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 ${iconBgClass} rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 ${iconTextClass}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="font-medium truncate text-night-900 dark:text-white">${v.title || 'Video'}</p>
                    <div class="flex items-center gap-3 text-xs text-night-500 dark:text-night-400">
                        <span class="${badgeBgClass} ${badgeTextClass} px-2 py-0.5 rounded-full text-xs">${v.platform || 'Social'}</span>
                        <span>@${v.uploader || 'unknown'}</span>
                        ${v.duration ? `<span>${formatDuration(v.duration)}</span>` : ''}
                    </div>
                </div>
                <a href="${API_BASE}/download/${v.filename}" class="bg-purple-500/20 text-purple-500 p-2 rounded-lg hover:bg-purple-500/30 transition-all duration-200" data-testid="download-social-${v.id}" download="${v.filename}">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                </a>
            </div>
        </div>
    `}).join('');
}

async function pollJobs() {
    try {
        const res = await fetch(`${API_BASE}/jobs`);
        jobs = await res.json();
        renderJobs();
        
        const hasActiveJobs = jobs.some(j => j.status === 'processing' || j.status === 'pending');
        if (hasActiveJobs) {
            setTimeout(pollJobs, 2000);
        }
    } catch (err) {
        console.error('Error polling jobs:', err);
    }
}

function renderJobs() {
    const splitJobsEl = document.getElementById('split-jobs');
    const mergeJobsEl = document.getElementById('merge-jobs');
    
    const splitJobs = jobs.filter(j => j.type === 'split');
    const mergeJobs = jobs.filter(j => j.type === 'merge');
    
    splitJobsEl.innerHTML = splitJobs.map(j => renderJobCard(j)).join('');
    mergeJobsEl.innerHTML = mergeJobs.map(j => renderJobCard(j)).join('');
}

function renderJobCard(job) {
    const statusClass = job.status === 'completed' ? 'completed' : 
                        job.status === 'error' ? 'error' : 'processing';
    
    const statusIcon = job.status === 'completed' ? 
        '<svg class="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>' :
        job.status === 'error' ? 
        '<svg class="w-5 h-5 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>' :
        '<svg class="w-5 h-5 text-primary spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>';
    
    let downloadButtons = '';
    if (job.status === 'completed') {
        if (job.type === 'split' && job.outputs) {
            downloadButtons = `
                <div class="flex flex-wrap gap-2 mt-3">
                    ${job.outputs.map((o, i) => `
                        <a href="${API_BASE}/download/${o}" class="inline-flex items-center gap-1 bg-primary/20 text-primary px-3 py-1 rounded-lg text-sm hover:bg-primary/30 transition-all duration-200" data-testid="download-segment-${i}">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                            </svg>
                            Segment ${i + 1}
                        </a>
                    `).join('')}
                </div>
            `;
        } else if (job.type === 'merge' && job.output) {
            downloadButtons = `
                <div class="mt-3">
                    <a href="${API_BASE}/download/${job.output}" class="inline-flex items-center gap-2 bg-success/20 text-success px-4 py-2 rounded-lg text-sm hover:bg-success/30 transition-all duration-200" data-testid="download-merged">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                        </svg>
                        Télécharger la vidéo fusionnée
                    </a>
                </div>
            `;
        }
    }
    
    return `
        <div class="job-card ${statusClass}" data-testid="job-${job.id}">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    ${statusIcon}
                    <div>
                        <p class="font-medium text-night-900 dark:text-white">${job.type === 'split' ? 'Découpe' : 'Fusion'}</p>
                        <p class="text-xs text-night-500 dark:text-night-400">${job.status === 'completed' ? 'Terminé' : job.status === 'error' ? 'Erreur' : 'En cours...'}</p>
                    </div>
                </div>
                ${job.status === 'processing' ? `
                    <div class="text-right">
                        <span class="text-lg font-bold text-primary">${job.progress || 0}%</span>
                    </div>
                ` : ''}
            </div>
            ${job.status === 'processing' ? `
                <div class="mt-3 h-2 bg-night-200 dark:bg-night-700 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300 rounded-full" style="width: ${job.progress || 0}%"></div>
                </div>
            ` : ''}
            ${downloadButtons}
            ${job.status === 'error' && job.error ? `<p class="mt-2 text-sm text-danger">${job.error}</p>` : ''}
        </div>
    `;
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const stats = await res.json();
        
        document.getElementById('stat-split').textContent = stats.totalVideosSplit || 0;
        document.getElementById('stat-segments').textContent = stats.totalSegmentsCreated || 0;
        document.getElementById('stat-merged').textContent = stats.totalVideosMerged || 0;
        document.getElementById('stat-time').textContent = Math.round((stats.totalTimeSaved || 0) / 60);
        
        renderAchievements(stats);
    } catch (err) {
        console.error('Error loading stats:', err);
    }
}

function renderAchievements(stats) {
    const achievements = [
        { id: 'first-split', name: 'Premier Découpage', desc: 'Découpez votre première vidéo', icon: '1', unlocked: stats.totalVideosSplit >= 1 },
        { id: 'first-merge', name: 'Première Fusion', desc: 'Fusionnez des vidéos pour la première fois', icon: '2', unlocked: stats.totalVideosMerged >= 1 },
        { id: 'segment-master', name: 'Maître des Segments', desc: 'Créez 10 segments', icon: '3', unlocked: stats.totalSegmentsCreated >= 10 },
        { id: 'video-pro', name: 'Video Pro', desc: 'Traitez 5 vidéos', icon: '4', unlocked: (stats.totalVideosSplit + stats.totalVideosMerged) >= 5 },
        { id: 'time-saver', name: 'Gain de Temps', desc: 'Traitez 10 minutes de vidéo', icon: '5', unlocked: stats.totalTimeSaved >= 600 }
    ];
    
    const container = document.getElementById('achievements');
    container.innerHTML = achievements.map(a => `
        <div class="achievement-card ${a.unlocked ? 'unlocked' : ''}" data-testid="achievement-${a.id}">
            <div class="achievement-icon ${a.unlocked ? 'bg-accent/30' : 'bg-indigo-800/50'}">
                ${a.unlocked ? a.icon : '?'}
            </div>
            <div class="flex-1">
                <p class="font-medium ${a.unlocked ? 'text-accent' : 'text-indigo-400'}">${a.name}</p>
                <p class="text-xs text-indigo-300">${a.desc}</p>
            </div>
            ${a.unlocked ? '<svg class="w-5 h-5 text-accent" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>' : ''}
        </div>
    `).join('');
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
