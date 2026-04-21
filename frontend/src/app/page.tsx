'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AlertCircle,
  ArrowRight,
  Bell,
  ChevronRight,
  Cloud,
  Cpu,
  Database,
  FileSearch,
  Gavel,
  Lock,
  Menu,
  MessageSquare,
  PenTool,
  Scale,
  Search,
  ShieldCheck,
  X,
} from 'lucide-react';

import styles from './page.module.css';

const news = [
  {
    tag: '서비스 출시',
    title: '계약서 독소조항 자동 탐색 엔진 업데이트',
    date: '2024.03.20',
    img: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=800',
  },
  {
    tag: '기능 추가',
    title: '직종별 맞춤 진정서 템플릿과 입력 흐름을 연결했습니다',
    date: '2024.03.15',
    img: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&q=80&w=800',
  },
  {
    tag: '공지사항',
    title: '무료 법률 상담 서비스와 Before·After 통합 랜딩을 공개했습니다',
    date: '2024.03.10',
    img: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=800',
  },
  {
    tag: '업데이트',
    title: '근로기준법 개정 반영과 단일 Vertex 환경 운영 기준 적용',
    date: '2024.03.05',
    img: 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&q=80&w=800',
  },
];

const categories = [
  { id: 'Featured', icon: ShieldCheck, label: 'Featured' },
  { id: 'Analysis', icon: Search, label: 'Analysis' },
  { id: 'Generator', icon: PenTool, label: 'Generator' },
  { id: 'Storage', icon: Database, label: 'Storage' },
  { id: 'Consulting', icon: MessageSquare, label: 'Consulting' },
  { id: 'Security', icon: Lock, label: 'Security' },
];

const featuredServices = [
  {
    title: '계약서 분석기',
    desc: '근로계약서 파일을 올리면 위험 조항과 권리 안내를 순차적으로 정리합니다.',
    icon: Search,
    href: '/before',
  },
  {
    title: '진정서 작성기',
    desc: '상황을 입력하면 조문 근거 답변과 문서 초안 흐름으로 이어집니다.',
    icon: FileSearch,
    href: '/after',
  },
  {
    title: '근로 기록 보관함',
    desc: '계약서와 증거 자료를 흐름에 따라 안전하게 정리하고 확인할 수 있습니다.',
    icon: Cloud,
    href: '/before',
  },
  {
    title: '노무사 매칭',
    desc: '추가 도움이 필요할 때 결과를 바탕으로 다음 조치를 준비할 수 있습니다.',
    icon: Scale,
    href: '/after',
  },
  {
    title: '맞춤형 알림',
    desc: '계약 검토와 문서 작성 흐름의 핵심 상태를 놓치지 않도록 안내합니다.',
    icon: Bell,
    href: '/before',
  },
];

const solutions = [
  { title: '부당 해고 대응', subtitle: '해고 예고 및 구제 신청 절차 안내', icon: AlertCircle, color: 'red' },
  { title: '임금 체불 해결', subtitle: '체불 임금 계산 및 고용노동부 진정', icon: Database, color: 'orange' },
  { title: '직장 내 괴롭힘', subtitle: '증거 수집 및 고충 처리 프로세스', icon: ShieldCheck, color: 'blue' },
  { title: '근로 시간 준수', subtitle: '연장·야간·휴일 수당 자동 계산', icon: Cpu, color: 'purple' },
  { title: '연차 유급 휴가', subtitle: '연차 발생 기준 및 사용 권리 확인', icon: Cloud, color: 'teal' },
];

function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`${styles.navbar} ${isScrolled ? styles.navbarScrolled : ''}`}>
      <div className={styles.navInner}>
        <Link href="/" className={styles.brand}>
          <span className={styles.brandMark}>
            <Gavel size={18} />
          </span>
          <span className={styles.brandText}>
            법대로 <span className={styles.brandSub}>law-main-road</span>
          </span>
        </Link>

        <div className={styles.navLinks}>
          <a href="#intro">소개</a>
          <a href="#services">서비스</a>
          <a href="#solutions">솔루션</a>
          <a href="#footer">가이드센터</a>
        </div>

        <div className={styles.navActions}>
          <Link href="/before" className={styles.loginButton}>
            Before
          </Link>
          <Link href="/after" className={styles.consoleButton}>
            After
          </Link>
        </div>

        <button className={styles.mobileMenuButton} onClick={() => setIsMenuOpen((value) => !value)} aria-label="메뉴 열기">
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      <AnimatePresence>
        {isMenuOpen ? (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className={styles.mobileMenu}
          >
            <a href="#intro">소개</a>
            <a href="#services">서비스</a>
            <a href="#solutions">솔루션</a>
            <Link href="/before">계약서 분석 시작</Link>
            <Link href="/after">진정서 작성 시작</Link>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </nav>
  );
}

function Hero() {
  return (
    <section id="intro" className={styles.hero}>
      <div className={styles.heroOverlay} />
      <div className={styles.heroOrbLeft} />
      <div className={styles.heroOrbRight} />
      <div className={styles.heroCircle} />
      <div className={styles.heroSquare} />
      <div className={styles.heroPlusOne}>+</div>
      <div className={styles.heroPlusTwo}>+</div>
      <div className={styles.heroPlusThree}>+</div>

      <div className={styles.heroContent}>
        <motion.div initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9 }}>
          <h2 className={styles.heroTitle}>
            더욱 강력해진 <span>법대로 AI</span>
          </h2>
          <p className={styles.heroDescription}>
            근로기준법 학습 데이터가 탑재된 법률 어시스턴트를 선보입니다.
            <br />
            계약서 분석부터 진정서 작성까지, 근로자의 모든 순간을 함께합니다.
          </p>
          <div className={styles.heroButtons}>
            <Link href="/before" className={styles.heroPrimary}>
              계약서 분석 시작
            </Link>
            <Link href="/after" className={styles.heroSecondary}>
              진정서 작성 시작
            </Link>
          </div>
        </motion.div>

        <div className={styles.heroDots}>
          <span className={styles.heroDotActive} />
          <span />
          <span />
        </div>
      </div>
    </section>
  );
}

function NewsSection() {
  return (
    <section className={styles.newsSection}>
      <div className={styles.container}>
        <div className={styles.sectionTop}>
          <h2>법대로의 최신 소식을 확인하세요</h2>
          <div className={styles.arrowButtons}>
            <button type="button" aria-label="이전">
              <ChevronRight size={18} className={styles.arrowLeft} />
            </button>
            <button type="button" aria-label="다음">
              <ChevronRight size={18} />
            </button>
          </div>
        </div>

        <div className={styles.newsGrid}>
          {news.map((item) => (
            <article key={item.title} className={styles.newsCard}>
              <div className={styles.newsImageWrap}>
                <img src={item.img} alt={item.title} className={styles.newsImage} />
                <div className={styles.newsImageOverlay} />
                <div className={styles.newsTag}>{item.tag}</div>
              </div>
              <h3>{item.title}</h3>
              <p>{item.date}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ServiceNav() {
  const [active, setActive] = useState('Featured');

  return (
    <section id="services" className={styles.serviceSection}>
      <div className={styles.container}>
        <div className={styles.serviceHeader}>
          <h2>
            효율적인 근로 권익 보호를 위한
            <br />
            다양한 서비스를 제공합니다
          </h2>
        </div>

        <div className={styles.serviceTabs}>
          {categories.map((category) => {
            const Icon = category.icon;
            const isActive = active === category.id;

            return (
              <button
                key={category.id}
                type="button"
                onClick={() => setActive(category.id)}
                className={isActive ? styles.serviceTabActive : styles.serviceTab}
              >
                <Icon size={22} />
                <span>{category.label}</span>
              </button>
            );
          })}
        </div>

        <div className={styles.serviceLayout}>
          <div className={styles.serviceFeature}>
            <div>
              <h3>{active}</h3>
              <p>
                가장 많이 찾는 {active} 서비스를 확인하고
                <br />
                당신의 소중한 권리를 지키세요.
              </p>
            </div>
            <div className={styles.serviceFeatureVisual}>
              <ShieldCheck size={84} />
            </div>
          </div>

          <div className={styles.serviceGrid}>
            {featuredServices.map((service) => {
              const Icon = service.icon;
              return (
                <Link key={service.title} href={service.href} className={styles.serviceCard}>
                  <div className={styles.serviceCardIcon}>
                    <Icon size={24} />
                  </div>
                  <div className={styles.serviceCardBody}>
                    <h4>
                      {service.title}
                      <span>Update</span>
                    </h4>
                    <p>{service.desc}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function SolutionCards() {
  return (
    <section id="solutions" className={styles.solutionSection}>
      <div className={styles.container}>
        <div className={styles.sectionTop}>
          <h2>
            비즈니스 특성을 고려한
            <br />
            법률 솔루션을 제안합니다
          </h2>
          <Link href="/after" className={styles.solutionButton}>
            솔루션 전체 보기
          </Link>
        </div>

        <div className={styles.solutionGrid}>
          {solutions.map((solution, index) => {
            const Icon = solution.icon;
            return (
              <article key={solution.title} className={styles.solutionCard}>
                <div className={`${styles.solutionIcon} ${styles[`solution${solution.color}` as keyof typeof styles]}`}>
                  <Icon size={44} strokeWidth={1.6} />
                </div>
                <h3>{solution.title}</h3>
                <p>{solution.subtitle}</p>
                <img
                  src={`https://images.unsplash.com/photo-15${index}9829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=500`}
                  alt={solution.title}
                  className={styles.solutionImage}
                />
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function PromotionBanners() {
  return (
    <section className={styles.promotionSection}>
      <div className={styles.container}>
        <div className={styles.promotionGrid}>
          <Link href="/before" className={`${styles.promoCard} ${styles.promoBlue}`}>
            <h4>계약서 분석 바로가기</h4>
            <p>
              업로드 후 분석을 시작하고
              <br />
              위험 조항과 권리 안내를 확인하세요.
            </p>
            <ArrowRight size={20} />
          </Link>
          <Link href="/after" className={`${styles.promoCard} ${styles.promoDark}`}>
            <h4>진정서 작성 바로가기</h4>
            <p>
              질문 입력부터 문서 초안까지
              <br />
              After 흐름으로 바로 이동합니다.
            </p>
            <ArrowRight size={20} />
          </Link>
          <Link href="/after" className={`${styles.promoCard} ${styles.promoLight}`}>
            <h4>신규 통합 구조</h4>
            <p>
              메인 랜딩 아래에서
              <br />
              Before와 After를 함께 운영합니다.
            </p>
            <ArrowRight size={20} />
          </Link>
        </div>
      </div>
    </section>
  );
}

function GlobalSection() {
  return (
    <section className={styles.globalSection}>
      <div className={styles.container}>
        <div className={styles.globalInner}>
          <div>
            <h3>국내외 근로자가 법대로 플랫폼을 통해 자신의 권익을 보호하고 있습니다.</h3>
            <p>계약 단계의 검토와 사후 대응 흐름을 하나의 메인 페이지에서 선택할 수 있습니다.</p>
          </div>
          <div className={styles.globalActions}>
            <Link href="/before" className={styles.globalButton}>
              Before 보기
            </Link>
            <div className={styles.avatarRow}>
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer id="footer" className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.footerGrid}>
          <div className={styles.footerBrandBlock}>
            <div className={styles.footerBrand}>
              <Gavel size={30} />
              <span>법대로</span>
            </div>
            <p>
              글로벌 근로자와 함께하며
              <br />
              정당한 권익 보호를 위해 앞장섭니다.
            </p>
            <div className={styles.footerIcons}>
              <span>
                <MessageSquare size={18} />
              </span>
              <span>
                <Search size={18} />
              </span>
              <span>
                <Bell size={18} />
              </span>
            </div>
          </div>

          <div className={styles.footerColumn}>
            <h4>Services</h4>
            <ul>
              <li>
                <Link href="/before">계약서 분석기</Link>
              </li>
              <li>
                <Link href="/after">진정서 작성기</Link>
              </li>
              <li>
                <Link href="/after">판례 검색</Link>
              </li>
              <li>
                <Link href="/after">상담 신청</Link>
              </li>
            </ul>
          </div>

          <div className={styles.footerColumn}>
            <h4>Company</h4>
            <ul>
              <li>
                <a href="#intro">회사소개</a>
              </li>
              <li>
                <a href="#services">서비스</a>
              </li>
              <li>
                <a href="#solutions">프레스킷</a>
              </li>
            </ul>
          </div>

          <div className={styles.footerColumn}>
            <h4>Support</h4>
            <ul>
              <li>
                <Link href="/before">Before 시작</Link>
              </li>
              <li>
                <Link href="/after">After 시작</Link>
              </li>
              <li>
                <a href="#footer">문의하기</a>
              </li>
            </ul>
          </div>

          <div className={styles.footerColumn}>
            <h4>Legal</h4>
            <ul>
              <li>
                <a href="#footer">이용약관</a>
              </li>
              <li>
                <a href="#footer">개인정보처리방침</a>
              </li>
              <li>
                <a href="#footer">법적 고지</a>
              </li>
            </ul>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <p>© 2024 법대로 (law-main-road) Corp. All rights reserved.</p>
          <div>
            <span>KR / EN</span>
            <span>Status</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function HomePage() {
  return (
    <div className={styles.page}>
      <Navbar />
      <Hero />
      <NewsSection />
      <ServiceNav />
      <SolutionCards />
      <PromotionBanners />
      <GlobalSection />
      <Footer />
    </div>
  );
}
