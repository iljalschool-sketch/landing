/* ===================================================================
   로직플로우 렌더러
   -------------------------------------------------------------------
   data/ 폴더의 JSON을 읽어 화면을 그립니다.
   콘텐츠를 수정할 때는 이 파일이 아니라 data/*.json을 고치세요.
   =================================================================== */
(() => {
    'use strict';

    /* ── 공통 유틸 ──────────────────────────────────────────────── */

    /** HTML 특수문자를 이스케이프한다 (의도치 않은 태그 삽입 방지). */
    const esc = (값) => String(값 ?? '').replace(/[&<>"']/g, (문자) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[문자]));

    /** 지정한 id의 요소에 HTML을 채운다. 요소가 없으면 조용히 넘어간다. */
    const 채우기 = (id, html) => {
        const 요소 = document.getElementById(id);
        if (요소) 요소.innerHTML = html;
    };

    /** JSON 파일을 읽는다. 실패 시 null을 반환하고 콘솔에 남긴다. */
    const 읽기 = async (이름) => {
        try {
            const 응답 = await fetch(`data/${이름}.json`, { cache: 'no-cache' });
            if (!응답.ok) throw new Error(`HTTP ${응답.status}`);
            return await 응답.json();
        } catch (오류) {
            console.error(`[로직플로우] data/${이름}.json 을 읽지 못했습니다:`, 오류);
            return null;
        }
    };

    /** 버튼·배지의 style 값을 Tailwind 클래스로 바꾼다. */
    const 스타일_클래스 = {
        kakao:   'bg-yellow-400 text-yellow-950 hover:bg-yellow-300',
        ghost:   'bg-white/10 backdrop-blur-md text-white border border-white/20 hover:bg-white/20',
        brand:   'bg-accent/20 text-accent border border-accent/20 hover:bg-accent/30',
        youtube: 'bg-red-600/20 text-red-300 border border-red-500/20 hover:bg-red-600/30',
        neutral: 'bg-slate-100 text-slate-700'
    };

    /* ── 1. 누적 성과 지표 ──────────────────────────────────────── */

    const 지표_그리기 = (자료) => {
        if (!자료) return;

        채우기('stats-heading', esc(자료.heading));
        채우기('stats-sub', esc(자료.subheading));
        채우기('stats-grid', 자료.items.map((항목) => `
            <div class="text-center">
                <i class="${esc(항목.icon)} text-2xl text-accent mb-4 block"></i>
                <p class="stat-value" data-target="${Number(항목.value)}">0</p>
                <p class="text-sm font-semibold text-slate-500 mt-2">${esc(항목.label)}</p>
            </div>
        `).join(''));

        // 접미사(명+, 회+ 등)는 카운트업이 끝난 뒤 붙이기 위해 따로 보관
        document.querySelectorAll('#stats-grid .stat-value').forEach((요소, 순번) => {
            요소.dataset.suffix = 자료.items[순번].suffix || '';
        });

        지표_카운트업_준비();
    };

    /** 지표가 화면에 들어올 때 0부터 목표값까지 숫자를 올린다. */
    const 지표_카운트업_준비 = () => {
        const 대상들 = document.querySelectorAll('.stat-value');
        const 모션_최소화 = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        const 표시 = (요소, 숫자) => {
            요소.textContent = 숫자.toLocaleString('ko-KR') + 요소.dataset.suffix;
        };

        // 애니메이션을 못 쓰거나 원치 않는 환경에서는 최종값만 바로 보여준다
        if (모션_최소화 || !('IntersectionObserver' in window)) {
            대상들.forEach((요소) => 표시(요소, Number(요소.dataset.target)));
            return;
        }

        const 관찰자 = new IntersectionObserver((항목들) => {
            항목들.forEach((항목) => {
                if (!항목.isIntersecting) return;
                관찰자.unobserve(항목.target);

                const 요소 = 항목.target;
                const 목표 = Number(요소.dataset.target);
                const 지속시간 = 1400;
                const 시작시각 = performance.now();

                const 한걸음 = (현재시각) => {
                    const 진행률 = Math.min((현재시각 - 시작시각) / 지속시간, 1);
                    // easeOutQuart : 처음엔 빠르고 끝에서 부드럽게 멈춘다
                    const 보정 = 1 - Math.pow(1 - 진행률, 4);
                    표시(요소, Math.round(목표 * 보정));
                    if (진행률 < 1) requestAnimationFrame(한걸음);
                };

                requestAnimationFrame(한걸음);
            });
        }, { threshold: 0.4 });

        대상들.forEach((요소) => 관찰자.observe(요소));
    };

    /* ── 2. 사업 영역 ───────────────────────────────────────────── */

    /* ── 해결하는 문제 ─────────────────────────────────────────── */

    const 문제_그리기 = (자료) => {
        // 항목이 없으면 섹션과 메뉴를 숨긴다
        if (!자료 || !자료.items || !자료.items.length) {
            const 섹션 = document.getElementById('problems');
            if (섹션) 섹션.style.display = 'none';
            const 메뉴 = document.querySelector('nav a[href="#problems"]');
            if (메뉴) 메뉴.style.display = 'none';
            return;
        }

        채우기('problems-heading', esc(자료.heading));
        채우기('problems-sub', esc(자료.subheading));
        채우기('problems-note', esc(자료.note || ''));
        채우기('problems-grid', 자료.items.map((문제) => `
            <div class="bg-white p-7 rounded-2xl border border-slate-100 shadow-sm card-hover">
                <div class="flex items-start gap-4 mb-4">
                    <div class="w-11 h-11 shrink-0 bg-mint text-brand rounded-xl flex items-center justify-center text-lg">
                        <i class="${esc(문제.icon)}"></i>
                    </div>
                    <div>
                        <p class="text-brand font-bold leading-snug">"${esc(문제.symptom)}"</p>
                        <p class="text-xs text-slate-400 mt-1 font-semibold">${esc(문제.title)}</p>
                    </div>
                </div>
                <p class="text-sm text-slate-600 leading-relaxed">${esc(문제.body)}</p>
            </div>
        `).join(''));
    };

    /* ── 2. 교육 · 솔루션 ──────────────────────────────────────── */

    const 사업영역_그리기 = (자료, 자동화) => {
        if (!자료) return;

        const 리포팅 = 자료.reporting;
        const 교육 = 자료.education;
        // 실제 개발한 건들. 없으면 courses.json의 features로 되돌아간다.
        const 개발목록 = 개발목록_만들기(자동화);

        // 섹션 제목 (교육 중심 포지셔닝)
        채우기('solutions-heading', esc(자료.heading || '교육 · 솔루션'));
        채우기('solutions-sub', esc(자료.subheading || ''));

        // 교육을 먼저, 개발·솔루션을 뒤에 그린다.
        // 실제 사업 비중이 교육 중심이므로 순서로도 드러낸다.
        채우기('solutions-grid', `
            <div class="bg-white p-10 rounded-3xl shadow-sm border-2 border-accent/30 card-hover group transition-all">
                <div class="w-14 h-14 bg-mint text-brand rounded-2xl flex items-center justify-center mb-6 text-2xl group-hover:bg-brand group-hover:text-white transition-colors">
                    <i class="${esc(교육.icon)}"></i>
                </div>
                <h3 class="text-2xl font-bold mb-1 group-hover:text-brand transition-colors">${esc(교육.title)}</h3>
                <p class="text-brand text-sm font-bold mb-4 italic">"${esc(교육.tagline)}"</p>
                <p class="text-slate-600 leading-relaxed mb-8">${교육.body}</p>

                <div class="space-y-4">
                    ${교육.open && 교육.open.length ? `
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">[수강 가능 교육]</p>
                        ${교육.open.map((과정) => {
                            // 링크가 없는 '개설 예정' 과정은 a 태그로 만들지 않는다 (빈 링크 방지)
                            const 속내용 = `
                                <p class="text-sm font-bold text-slate-900">${esc(과정.title)}</p>
                                ${과정.cta ? `<p class="text-xs text-brand mt-1 font-semibold">${esc(과정.cta)}</p>` : ''}`;
                            return 과정.url
                                ? `<a href="${esc(과정.url)}" target="_blank" rel="noopener"
                                      class="block p-4 bg-slate-50 rounded-xl hover:bg-mint transition border border-transparent hover:border-accent">${속내용}</a>`
                                : `<div class="p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200 opacity-80">${속내용}</div>`;
                        }).join('')}
                    ` : ''}

                    ${교육.classrooms && 교육.classrooms.length ? `
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">[수강생 전용 페이지]</p>
                        ${교육.classrooms.map((강의실) => `
                            <a href="${esc(강의실.url)}"
                               class="block p-4 bg-mint rounded-xl hover:bg-accent/20 transition border border-accent">
                                <p class="text-sm font-bold text-slate-900">${esc(강의실.title)}</p>
                                <p class="text-xs text-brand mt-1 font-semibold">${esc(강의실.cta)}</p>
                            </a>
                        `).join('')}
                    ` : ''}
                </div>
            </div>

            <a href="${esc(리포팅.url)}" class="block bg-white p-10 rounded-3xl shadow-sm border border-slate-100 card-hover group transition-all">
                <div class="w-14 h-14 bg-mint text-brand rounded-2xl flex items-center justify-center mb-6 text-2xl group-hover:bg-brand group-hover:text-white transition-colors">
                    <i class="${esc(리포팅.icon)}"></i>
                </div>
                <h3 class="text-2xl font-bold mb-4 group-hover:text-brand transition-colors">
                    ${esc(리포팅.title)}
                    <i class="fas fa-arrow-right ml-2 text-sm opacity-0 group-hover:opacity-100 transition-all"></i>
                </h3>
                <p class="text-slate-600 leading-relaxed mb-8">${리포팅.body}</p>
                ${개발목록 || 리포팅.features.map((특징) => `
                    <div class="flex items-start mb-3">
                        <i class="fas fa-check-circle text-accent mt-1 mr-3"></i>
                        <span class="text-sm text-slate-700 font-medium">${esc(특징)}</span>
                    </div>
                `).join('')}
            </a>
        `);
    };

    /**
     * 솔루션 카드 안에 실제 개발한 건들을 보여준다.
     *
     * '반복 업무 자동화 프로그램 개발' 같은 일반적인 홍보 문구보다
     * 실제로 만든 것의 이름이 훨씬 설득력이 있다.
     */
    const 개발목록_만들기 = (자동화) => {
        if (!자동화 || !자동화.groups || !자동화.groups.length) return '';

        return 자동화.groups.map((그룹) => `
            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                ${esc(그룹.label)}
            </p>
            <div class="space-y-2 mb-6">
                ${그룹.items.map((항목) => `
                    <div class="flex items-start">
                        <i class="fas fa-check-circle text-accent mt-1 mr-3 shrink-0"></i>
                        <span class="text-sm text-slate-700">
                            ${esc(항목.title)}
                            ${항목.client ? `<span class="text-slate-400 text-xs ml-1">(${esc(항목.client)})</span>` : ''}
                        </span>
                    </div>
                `).join('')}
            </div>
        `).join('');
    };

    /* ── 개발 사례 ─────────────────────────────────────────────── */

    const 사례_그리기 = (자료) => {
        if (!자료 || !자료.items || !자료.items.length) {
            const 섹션 = document.getElementById('cases');
            if (섹션) 섹션.style.display = 'none';
            return;
        }

        채우기('cases-heading', esc(자료.heading));
        채우기('cases-sub', esc(자료.subheading));

        채우기('cases-list', 자료.items.map((사례, 순번) => {
            // 숫자로 보여줄 수 있는 사례만 before → after 를 띄운다
            const 지표 = 사례.metric ? `
                <div class="flex items-center gap-3 mt-4 text-sm">
                    <span class="text-slate-500">${esc(사례.metric.label)}</span>
                    <span class="text-slate-400 line-through">${esc(사례.metric.from)}</span>
                    <i class="fas fa-arrow-right text-point text-xs"></i>
                    <span class="text-point font-bold">${esc(사례.metric.to)}</span>
                </div>` : '';

            const 상세 = ['before', 'approach', 'result']
                .filter((열쇠) => 사례[열쇠])
                .map((열쇠) => `
                    <div class="mb-5 last:mb-0">
                        <p class="text-xs font-bold text-point mb-2">${{
                            before: '이전에는',
                            approach: '이렇게 바꿨습니다',
                            result: '그래서'
                        }[열쇠]}</p>
                        <p class="text-slate-300 text-sm leading-relaxed">${esc(사례[열쇠])}</p>
                    </div>`).join('');

            return `
                <div class="case-card bg-white/5 rounded-2xl border border-white/10 overflow-hidden transition hover:border-point/40"
                     data-case="${순번}">
                    <button class="w-full text-left p-7 flex items-start justify-between gap-4" aria-expanded="false">
                        <div>
                            <h3 class="text-lg font-bold text-white mb-2">${esc(사례.title)}</h3>
                            <p class="text-slate-400 text-sm leading-relaxed">${esc(사례.summary)}</p>
                            ${지표}
                        </div>
                        <i class="fas fa-chevron-down text-slate-500 mt-1 shrink-0 case-arrow transition-transform"></i>
                    </button>
                    <div class="case-detail px-7">
                        <div class="border-t border-white/10 pt-6 pb-7">
                            ${상세}
                            ${사례.tech ? `<p class="text-xs text-slate-500 mt-6">${esc(사례.tech)}</p>` : ''}
                        </div>
                    </div>
                </div>`;
        }).join(''));

        채우기('cases-note', `
            <p class="text-slate-300 leading-relaxed">${esc(자료.note || '')}</p>`);

        사례_토글_연결();
    };

    /** 사례 카드를 눌러 상세를 펼친다 (여러 개를 동시에 열 수 있다). */
    const 사례_토글_연결 = () => {
        document.querySelectorAll('.case-card').forEach((카드) => {
            const 버튼 = 카드.querySelector('button');
            버튼.addEventListener('click', () => {
                const 열림 = 카드.classList.toggle('open');
                버튼.setAttribute('aria-expanded', String(열림));
                카드.querySelector('.case-arrow').style.transform =
                    열림 ? 'rotate(180deg)' : '';
            });
        });
    };

    /* ── 3. 소개 영상 & 아키텍트 ────────────────────────────────── */

    const 소개_그리기 = (자료) => {
        if (!자료) return;

        const 영상 = 자료.introVideo;
        const 소개 = 자료.about;

        채우기('intro-video-body', `
            <div class="section-head mb-10">
                <p class="eyebrow">Watch</p>
                <h2 class="section-title">${esc(영상.heading)}</h2>
                <p class="section-lead">${esc(영상.subheading)}</p>
            </div>
            <div class="relative aspect-video rounded-2xl overflow-hidden shadow-xl ring-1 ring-black/5">
                <iframe class="absolute top-0 left-0 w-full h-full"
                        src="https://www.youtube.com/embed/${esc(영상.youtubeId)}"
                        title="${esc(영상.title)}" frameborder="0" loading="lazy"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen></iframe>
            </div>
        `);

        채우기('about-body', `
            <div class="about-photo rounded-2xl overflow-hidden flex-shrink-0 shadow-xl ring-1 ring-white/10 bg-gradient-to-br from-growth to-deep">
                <img src="${esc(소개.photo)}" alt="${esc(소개.name)}" class="w-full h-full object-cover"
                     data-fallback="images/brand/symbol-white.png">
            </div>
            <div>
                <p class="eyebrow mb-3" style="color: var(--point-yellow)">${esc(소개.eyebrow)}</p>
                <h3 class="text-3xl md:text-4xl font-extrabold mb-6 tracking-tight">
                    ${esc(소개.name)} <span class="text-xl font-normal text-slate-400">| ${esc(소개.alias)}</span>
                </h3>
                <p class="text-slate-300 leading-relaxed mb-8 text-lg">
                    "${소개.quote}"<br><br>${소개.body}
                </p>
                <div class="flex flex-wrap gap-2.5">
                    ${소개.tags.map((태그) => `
                        <span class="px-4 py-1.5 bg-white/10 rounded-lg text-sm font-medium border border-white/10">${esc(태그)}</span>
                    `).join('')}
                </div>
            </div>
        `);

        프로필사진_대체_연결();
    };

    /** 프로필 사진 파일이 없으면 브랜드 심볼로 대체한다. */
    const 프로필사진_대체_연결 = () => {
        document.querySelectorAll('img[data-fallback]').forEach((이미지) => {
            이미지.addEventListener('error', () => {
                이미지.src = 이미지.dataset.fallback;
                이미지.className = 'w-28 h-28 object-contain opacity-80';
                이미지.removeAttribute('data-fallback');   // 무한 반복 방지
            }, { once: true });
        });
    };

    /* ── 4. 활동사진 갤러리 ─────────────────────────────────────── */

    const 갤러리_그리기 = (자료) => {
        // 사진이 없으면 섹션과 메뉴 링크를 통째로 숨긴다
        // (준비 중인 빈 갤러리가 노출되지 않도록)
        if (!자료 || !자료.items || !자료.items.length) {
            const 섹션 = document.getElementById('gallery');
            if (섹션) 섹션.style.display = 'none';
            const 메뉴 = document.querySelector('nav a[href="#gallery"]');
            if (메뉴) 메뉴.style.display = 'none';
            return;
        }

        채우기('gallery-heading', esc(자료.heading));
        채우기('gallery-sub', esc(자료.subheading));
        채우기('gallery-grid', 자료.items.map((사진, 순번) => `
            <figure class="gallery-item" data-index="${순번}" tabindex="0" role="button"
                    aria-label="${esc(사진.caption)} 크게 보기">
                <img src="images/gallery/thumb/${esc(사진.file)}"
                     alt="${esc(사진.caption)}" loading="lazy" decoding="async">
                <figcaption class="gallery-caption">${esc(사진.caption)}</figcaption>
            </figure>
        `).join(''));

        갤러리_라이트박스_연결(자료.items);
    };

    /** 사진을 클릭하면 원본을 크게 띄운다. */
    const 갤러리_라이트박스_연결 = (사진들) => {
        const 라이트박스 = document.getElementById('lightbox');
        const 이미지 = document.getElementById('lightbox-img');
        const 설명 = document.getElementById('lightbox-caption');
        if (!라이트박스 || !사진들.length) return;

        let 현재 = 0;

        const 열기 = (순번) => {
            현재 = (순번 + 사진들.length) % 사진들.length;
            이미지.src = `images/gallery/${사진들[현재].file}`;
            이미지.alt = 사진들[현재].caption;
            설명.textContent = `${사진들[현재].caption} (${현재 + 1}/${사진들.length})`;
            라이트박스.classList.add('show');
            document.body.style.overflow = 'hidden';
        };

        const 닫기 = () => {
            라이트박스.classList.remove('show');
            document.body.style.overflow = '';
        };

        document.querySelectorAll('.gallery-item').forEach((항목) => {
            const 순번 = Number(항목.dataset.index);
            항목.addEventListener('click', () => 열기(순번));
            항목.addEventListener('keydown', (사건) => {
                if (사건.key === 'Enter' ||사건.key === ' ') {
                    사건.preventDefault();
                    열기(순번);
                }
            });
        });

        라이트박스.addEventListener('click', (사건) => {
            if (사건.target.closest('[data-prev]')) return 열기(현재 - 1);
            if (사건.target.closest('[data-next]')) return 열기(현재 + 1);
            if (사건.target === 이미지) return;    // 사진 자체를 누른 건 무시
            닫기();
        });

        document.addEventListener('keydown', (사건) => {
            if (!라이트박스.classList.contains('show')) return;
            if (사건.key === 'Escape') 닫기();
            if (사건.key === 'ArrowLeft') 열기(현재 - 1);
            if (사건.key === 'ArrowRight') 열기(현재 + 1);
        });
    };

    /* ── 5. 경력 탭 ─────────────────────────────────────────────── */

    /** 경력 탭 본문을 감싸는 공통 카드 틀 */
    const 탭_카드 = (아이콘, 제목, 부제, 본문) => `
        <div class="bg-white/5 backdrop-blur-sm rounded-3xl border border-white/10 p-8 md:p-12">
            <div class="flex items-center mb-8">
                <div class="w-12 h-12 bg-accent/20 text-accent rounded-2xl flex items-center justify-center text-xl mr-4">
                    <i class="${아이콘}"></i>
                </div>
                <div>
                    <h3 class="text-2xl font-bold">${esc(제목)}</h3>
                    ${부제 ? `<p class="text-slate-400 text-sm mt-1">${esc(부제)}</p>` : ''}
                </div>
            </div>
            ${본문}
        </div>`;

    const 학력_그리기 = (자료) => {
        if (!자료) return;

        const 본문 = `<div class="space-y-6">${자료.items.map((항목, 순번) => `
            <div class="flex items-start gap-4">
                <div class="w-3 h-3 rounded-full mt-2 flex-shrink-0"
                     style="background: var(--light-green); opacity: ${Math.max(1 - 순번 * 0.25, 0.35)}"></div>
                <div>
                    <p class="text-lg font-bold text-white">${esc(항목.school)}</p>
                    <p class="text-slate-400 mt-1">${esc(항목.degree)}</p>
                </div>
            </div>
        `).join('')}</div>`;

        채우기('tab-education', 탭_카드('fas fa-graduation-cap', '학력 사항', null, 본문));
    };

    /**
     * 모집이 마감됐는지 확인한다.
     *
     * 원래는 엑셀 변환(build_lectures.py) 때 걸러지지만, 변환·배포를 깜빡해도
     * 끝난 과정이 '신청 가능'으로 남지 않도록 화면에서 한 번 더 확인한다.
     */
    const 모집_마감됨 = (강의) => {
        if (!강의.expires) return false;
        const 마감일 = new Date(`${강의.expires}T23:59:59`);
        return !Number.isNaN(마감일.getTime()) && 마감일 < new Date();
    };

    /** 강의 항목 옆에 붙는 작은 배지들 (모집상태 · 형태 · 반복 횟수) */
    const 배지_모양 = {
        '신청가능': { 글: '신청 가능',  색: 'bg-accent text-white' },
        '오픈예정': { 글: '개설 예정',  색: 'bg-amber-400/90 text-amber-950' },
        '온라인':   { 글: '온라인',     색: 'bg-sky-400/90 text-sky-950' },
        'VOD':      { 글: 'VOD',        색: 'bg-violet-400/90 text-violet-950' }
    };

    const 배지 = (강의) => {
        const 조각들 = [];
        const 붙이기 = (열쇠) => {
            const 모양 = 배지_모양[열쇠];
            if (모양) {
                조각들.push(`<span class="ml-2 px-2 py-0.5 rounded-full ${모양.색} text-xs font-bold align-middle">${모양.글}</span>`);
            }
        };

        붙이기(강의.status);
        붙이기(강의.format);
        if (강의.count > 1) {
            조각들.push(`<span class="ml-2 px-2 py-0.5 rounded-full bg-accent/15 text-accent text-xs font-bold align-middle">${esc(강의.count)}회</span>`);
        }
        return 조각들.join('');
    };

    // 주의: 경유 에이전시명은 lectures.json에 아예 담지 않는다. data/*.json은
    //       주소만 알면 누구나 내려받을 수 있어 '안 그리는 것'으로는 비공개가 되지
    //       않는다. 기록은 저장소 밖 엑셀에만 있다. 표기 기준은 해당 파일의 _표기원칙 참고.
    const 강의_그리기 = (자료) => {
        if (!자료) return;

        const 본문 = 자료.groups.map((그룹) => {
            const 항목들 = 그룹.items.filter((강의) => !모집_마감됨(강의));
            if (!항목들.length) return '';      // 전부 마감됐으면 제목도 숨긴다
            return `
            <p class="text-xs font-bold uppercase tracking-wider mb-4 ${그룹.highlight ? 'text-accent' : 'text-slate-400'}">
                ${esc(그룹.label)}
            </p>
            <div class="space-y-3 mb-10">
                ${항목들.map((강의) => {
                    const 내용 = `
                        <p class="${그룹.highlight ? 'text-white font-bold' : 'text-slate-200'}">
                            ${esc(강의.title)}
                            ${강의.client ? `<span class="${그룹.highlight ? 'text-accent' : 'text-slate-500'} text-sm ml-1">(${esc(강의.client)})</span>` : ''}
                            ${배지(강의)}
                            ${강의.year ? `<span class="text-slate-500 text-xs ml-2">${esc(강의.year)}</span>` : ''}
                        </p>
                        ${강의.target ? `<p class="text-slate-500 text-xs mt-1">교육 대상 · ${esc(강의.target)}</p>` : ''}
                        ${강의.url && 강의.status === '신청가능'
                            ? '<p class="text-accent text-xs mt-1 font-bold">신청하러 가기 →</p>' : ''}`;
                    const 클래스 = `career-item${그룹.highlight ? ' highlight' : ''}`;

                    return 강의.url
                        ? `<a href="${esc(강의.url)}" target="_blank" rel="noopener" class="${클래스} block">${내용}</a>`
                        : `<div class="${클래스}">${내용}</div>`;
                }).join('')}
            </div>
        `;
        }).join('');

        채우기('tab-lectures', 탭_카드('fas fa-chalkboard-teacher', '강의 이력', null, 본문));
    };

    const 자동화_그리기 = (자료) => {
        if (!자료) return;

        const 본문 = 자료.groups.map((그룹) => `
            <p class="text-xs font-bold uppercase tracking-wider mb-4 ${그룹.highlight ? 'text-accent' : 'text-slate-400'}">
                ${esc(그룹.label)}
            </p>
            <div class="${그룹.layout === 'grid' ? 'grid md:grid-cols-2 gap-3' : 'space-y-3'} mb-10">
                ${그룹.items.map((항목) => `
                    <div class="career-item${그룹.highlight ? ' highlight' : ''}">
                        <p class="${그룹.highlight ? 'text-white font-bold' : 'text-slate-200 text-sm'}">
                            ${esc(항목.title)}
                            ${항목.client ? `<span class="text-slate-500 text-xs ml-1">(${esc(항목.client)})</span>` : ''}
                            ${!그룹.highlight && 항목.tech ? `<span class="text-slate-500 text-xs ml-1">· ${esc(항목.tech)}</span>` : ''}
                        </p>
                        ${그룹.highlight && 항목.tech ? `<p class="text-accent text-xs mt-1">${esc(항목.tech)}</p>` : ''}
                        ${항목.effect ? `
                            <p class="text-slate-400 text-xs mt-2 leading-relaxed">
                                <span class="text-accent">해결</span> ${esc(항목.effect)}
                            </p>` : ''}
                    </div>
                `).join('')}
            </div>
        `).join('');

        채우기('tab-automation', 탭_카드('fas fa-cogs', '자동화 프로그램 개발', null, 본문));
    };

    const 유튜브_그리기 = (자료) => {
        if (!자료) return;

        const 채널 = 자료.channel;
        const 시리즈들 = 자료.series;

        const 본문 = `
            <div class="flex flex-wrap gap-3 mb-10">
                ${채널.links.map((링크) => `
                    <a href="${esc(링크.url)}" ${링크.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}
                       class="inline-flex items-center px-5 py-2.5 rounded-full text-sm font-bold transition ${스타일_클래스[링크.style] || 스타일_클래스.brand}">
                        <i class="${esc(링크.icon)} mr-2"></i>${esc(링크.label)}
                    </a>
                `).join('')}
            </div>

            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-6">
                영상 시리즈 <span class="text-slate-500 font-normal">(카드를 클릭하면 영상 목록이 열립니다)</span>
            </p>
            <div class="grid sm:grid-cols-2 gap-4" id="series-grid">
                ${시리즈들.map((시리즈) => `
                    <div class="series-card bg-white/5 rounded-2xl p-6 border border-white/5 hover:border-accent transition">
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="text-3xl mb-3"><i class="${esc(시리즈.icon)} text-accent"></i></div>
                                <p class="font-bold text-white mb-1">${esc(시리즈.title)}</p>
                                <p class="text-slate-400 text-sm">
                                    ${esc(시리즈.desc)}
                                    <span class="text-accent text-xs">(${시리즈.videos.length}편)</span>
                                </p>
                            </div>
                            <i class="fas fa-chevron-down text-slate-500 series-arrow transition-transform"></i>
                        </div>
                        <div class="video-list">
                            <div class="border-t border-white/10 pt-4 mt-4 space-y-1">
                                ${시리즈.videos.map((영상, 순번) => `
                                    <a href="https://www.youtube.com/watch?v=${esc(영상.id)}" target="_blank" rel="noopener" class="video-link">
                                        <span class="video-num">${순번 + 1}</span>${esc(영상.title)}
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>`;

        채우기('tab-youtube', 탭_카드('fab fa-youtube', 채널.name, 채널.desc, 본문));
        시리즈_토글_연결();
    };

    /** 시리즈 카드를 누르면 영상 목록을 펼친다 (한 번에 하나만). */
    const 시리즈_토글_연결 = () => {
        document.querySelectorAll('.series-card').forEach((카드) => {
            카드.addEventListener('click', (사건) => {
                if (사건.target.closest('.video-link')) return;   // 영상 링크 클릭은 통과

                const 목록 = 카드.querySelector('.video-list');
                const 열려있음 = 목록.classList.contains('show');

                // 열려 있던 다른 카드는 모두 닫는다
                document.querySelectorAll('.video-list.show').forEach((다른목록) => {
                    const 다른카드 = 다른목록.closest('.series-card');
                    다른목록.classList.remove('show');
                    다른카드.classList.remove('expanded');
                    다른카드.querySelector('.series-arrow').style.transform = '';
                });

                if (!열려있음) {
                    목록.classList.add('show');
                    카드.classList.add('expanded');
                    카드.querySelector('.series-arrow').style.transform = 'rotate(180deg)';
                }
            });
        });
    };

    /* ── 6. 연락처 ──────────────────────────────────────────────── */

    const 연락처_그리기 = (자료) => {
        if (!자료) return;

        const 연락처 = 자료.contact;

        채우기('contact-heading', esc(연락처.heading));
        채우기('contact-grid', 연락처.channels.map((채널) => {
            const 배경 = {
                kakao:   'bg-yellow-50 border-yellow-100 hover:bg-yellow-100 text-yellow-600',
                brand:   'bg-slate-50 border-slate-100 hover:bg-mint text-brand',
                youtube: 'bg-red-50 border-red-100 hover:bg-red-100 text-red-600',
                neutral: 'bg-slate-50 border-slate-100 text-slate-400'
            }[채널.style] || 'bg-slate-50 border-slate-100 text-brand';

            const 내용 = `
                <i class="${esc(채널.icon)} text-3xl mb-4 block"></i>
                <span class="text-sm font-bold text-slate-900 uppercase">${esc(채널.label)}</span>
                <p class="text-xs text-slate-500 mt-1">${esc(채널.desc)}</p>`;
            const 클래스 = `p-6 rounded-2xl border transition ${배경}`;

            return 채널.url
                ? `<a href="${esc(채널.url)}" ${채널.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''} class="${클래스}">${내용}</a>`
                : `<div class="${클래스}">${내용}</div>`;
        }).join(''));

        채우기('contact-copyright', esc(연락처.copyright));
    };

    /* ── 7. 경력 탭 전환 ────────────────────────────────────────── */

    const 탭_전환_연결 = () => {
        document.querySelectorAll('.tab-btn').forEach((버튼) => {
            버튼.addEventListener('click', () => {
                document.querySelectorAll('.tab-content').forEach((내용) => 내용.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach((다른버튼) => 다른버튼.classList.remove('active'));

                const 대상 = document.getElementById('tab-' + 버튼.dataset.tab);
                if (대상) 대상.classList.add('active');
                버튼.classList.add('active');
            });
        });
    };

    /* ── 시작 ───────────────────────────────────────────────────── */

    const 시작 = async () => {
        const 파일들 = ['site', 'stats', 'courses', 'gallery', 'education',
                        'lectures', 'automation', 'videos', 'problems', 'cases'];
        const [사이트, 지표, 과정, 갤러리, 학력, 강의, 자동화, 영상, 문제, 사례] =
            await Promise.all(파일들.map(읽기));

        지표_그리기(지표);
        문제_그리기(문제);
        사업영역_그리기(과정, 자동화);
        사례_그리기(사례);
        소개_그리기(사이트);
        갤러리_그리기(갤러리);
        학력_그리기(학력);
        강의_그리기(강의);
        자동화_그리기(자동화);
        유튜브_그리기(영상);
        연락처_그리기(사이트);
        탭_전환_연결();

        document.body.classList.add('loaded');
    };

    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', 시작)
        : 시작();
})();
