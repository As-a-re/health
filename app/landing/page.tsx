"use client"

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Menu, X } from "lucide-react"
import { useState } from "react"

const translations: Record<string, Record<string, string>> = {
  en: {
    features: "Features",
    how: "How it works",
    about: "About",
    contact: "Contact",
    tagline: "We Build Healthy For Wealthy Living",
    heading: "HEALTH",
    description:
      "Let’s build a healthier world for everyone. Get personalized AI-powered health guidance in English and Akan — fast, private, and reliable.",
    cta_primary: "Get Started for Free",
    cta_toggle: "View in Akan",
    access_title: "24/7 Access",
    access_sub: "Support whenever you need it",
    multilingual_title: "Multilingual",
    multilingual_sub: "English & Akan supported",
    feature1_title: "AI Symptom Checker",
    feature1_desc:
      "Describe your symptoms by typing or speaking and receive a clear, evidence-informed explanation and next steps.",
    feature2_title: "Multilingual Support",
    feature2_desc: "Seamless English ↔ Akan support with voice input and output to serve local communities.",
    feature3_title: "Secure & Private",
    feature3_desc: "Your health data stays on our secure servers. We prioritize privacy and encryption by design.",
    how1_title: "Create an Account",
    how1_desc: "Sign up quickly and choose your preferred language.",
    how2_title: "Ask Your Question",
    how2_desc: "Type or speak your health concerns and upload images if needed.",
    how3_title: "Get Guidance",
    how3_desc: "Receive a clear answer with suggested next steps and educational resources.",
    about_title: "About HEALTH",
    about_p1:
      "HEALTH is an AI-powered assistant built to increase access to trustworthy health information for everyone. We focus on accessibility, local language support, and privacy.",
    about_p2: "Our mission is to give people the tools to make informed health decisions and connect them to care when needed.",
    contact_title: "Contact Us",
    contact_sub:
      "Have questions, feedback or need support? Send us a message and we’ll get back to you.",
    name_placeholder: "Your name",
    email_placeholder: "Email address",
    message_placeholder: "How can we help?",
    send_button: "Send Message",
    mobile_cta: "Get Started",
  },
  ak: {
    features: "Nkyerɛmu",
    how: "Sɛ ɛyɛ adwuma",
    about: "Yɛn Ho",
    contact: "Frɛ Yɛn",
    tagline: "Yɛbɔ nkwa ma asetena pa",
    heading: "APƆWMUDEN",
    description:
      "Momma yɛn nsiesie wiase a ɛyɛ apɔwmuden ma obiara. Fa adwuma yi na nya apɔwmuden nsɛm a ɛfata wo wɔ Akan ne Borɔfo mu — ntɛm, fa ho ban, na ɛyɛ nokware.",
    cta_primary: "Hyɛ ase (Ɛnni sika)",
    cta_toggle: "Hwɛ wɔ Akan mu",
    access_title: "Akwankyerɛ da biara",
    access_sub: "Boa wo bere biara a wopɛ",
    multilingual_title: "Kasa bebree",
    multilingual_sub: "English ne Akan mu boa",
    feature1_title: "AI Nsɛnhyɛsoɔ",
    feature1_desc:
      "Kyerɛ nsɛnhyɛsoɔ no — kasa anaa kyerɛw — na nya nsɛm a ɛkyerɛ asɛm no ho ne nea wobɛyɛ akyi.",
    feature2_title: "Kasa Mpɔtam",
    feature2_desc: "English ↔ Akan kasa mu boa, ka anaa tie wɔ kasa mu.",
    feature3_title: "Ahodwiri ne Asomdwoe",
    feature3_desc: "Wo apɔwmuden data bɛda so wɔ asomdwoe mu. Yɛde privasi ne encryption di kan.",
    how1_title: "Bɔ Akawnt",
    how1_desc: "Kɔ so na paw kasa a wopɛ.",
    how2_title: "Bisa wo nsɛm",
    how2_desc: "Kyerɛw anaa kasa wo nsɛm, na fa mfonini sɛ ɛsɛ.",
    how3_title: "Fa akwankyerɛ",
    how3_desc: "Fa akwankyerɛ a ɛkyerɛ nea wobɛyɛ ne nsɛm a ɛho hia.",
    about_title: "Fa HEALTH ho",
    about_p1:
      "HEALTH yɛ AI a ɛboa ma obiara nya apɔwmuden nsɛm a wɔtumi gye di. Yɛde mfaso a ɛwɔ accessibility, kasa mpɔtam, ne ahodwiri bɔ mu.",
    about_p2: "Yɛn botae ne sɛ yɛma nnipa nya akwankyerɛ a ɛma wɔn tumi yɛ apɔwmuden mu nsɛm pa.",
    contact_title: "Frɛ Yɛn",
    contact_sub: "Wɔwɔ nsɛmmisa anaa mmoa? Fa asɛm kyerɛ yɛn na yɛbɛsan akyerɛ wo.",
    name_placeholder: "Wo din",
    email_placeholder: "Email",
    message_placeholder: "Ɔkwan a yɛbɛboa wo?",
    send_button: "Som Asɛm",
    mobile_cta: "Hyɛ ase",
  },
}

export default function LandingPage() {
  const [lang, setLang] = useState('en' as 'en' | 'ak')
  const [open, setOpen] = useState(false)
  const t = (key: string) => translations[lang][key] || key

  // Smooth scroll helper for in-page anchors
  const scrollToSection = (id: string) => (e: any) => {
    try {
      e.preventDefault()
    } catch {}
    const el = document.getElementById(id)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      // fallback: change hash
      window.location.hash = `#${id}`
    }
    setOpen(false)
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-white to-sky-50">
      <style>{`
        @keyframes floatY {0% { transform: translateY(0px);} 50% { transform: translateY(-12px);} 100% { transform: translateY(0px);} }
        .dna-float { animation: floatY 5s ease-in-out infinite; }
        .blob { filter: blur(40px); opacity: 0.8; }
      `}</style>

      <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 mx-auto">
        {/* Top navigation */}
        <nav className="flex items-center justify-between py-6">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-tr from-blue-600 to-teal-400 rounded-lg shadow-md text-white">
                <svg width="36" height="36" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                  <rect width="48" height="48" rx="10" fill="url(#lgLogo)" />
                  <defs>
                    <linearGradient id="lgLogo" x1="0" x2="1">
                      <stop offset="0" stopColor="#67b3ff" />
                      <stop offset="1" stopColor="#9be7ff" />
                    </linearGradient>
                  </defs>
                  <g transform="translate(6,6)">
                    <path d="M6 4 L12 4 L14 12 L10 12 L8 8 L6 12 L2 12 L4 4 Z" fill="white" opacity="0.96" />
                  </g>
                </svg>
              </div>
              <div>
                <div className="text-lg font-extrabold text-slate-900 tracking-tight">{t("heading")}</div>
                <div className="text-xs text-slate-500">{t("tagline")}</div>
              </div>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-6 text-sm text-slate-600">
            <a href="#features" onClick={scrollToSection('features')} className="hover:text-slate-900">{t("features")}</a>
            <a href="#how" onClick={scrollToSection('how')} className="hover:text-slate-900">{t("how")}</a>
            <a href="#about" onClick={scrollToSection('about')} className="hover:text-slate-900">{t("about")}</a>
            <a href="#contact" onClick={scrollToSection('contact')} className="hover:text-slate-900">{t("contact")}</a>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-3">
              <Link href="/login" className="text-sm text-slate-700 hover:underline">{lang === "en" ? "Sign In" : "Kɔ mu"}</Link>
              <Link href="/register">
                <Button size="sm" className="bg-gradient-to-r from-blue-600 to-teal-400 text-white shadow-md">{t("cta_primary")}</Button>
              </Link>
              <Button size="sm" variant="outline" className="px-3 py-2" onClick={() => setLang(lang === "en" ? "ak" : "en")}>{lang === "en" ? t("cta_toggle") : "View in English"}</Button>
            </div>

            {/* Mobile menu button */}
            <button className="md:hidden p-2 rounded-md border border-slate-200" onClick={() => setOpen(!open)} aria-label="Toggle menu">
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </nav>

        {/* Mobile nav panel */}
        {open && (
          <div className="md:hidden bg-white rounded-xl shadow-lg p-4 mb-6">
            <div className="flex flex-col gap-3">
              <a href="#features" onClick={scrollToSection('features')} className="py-2">{t("features")}</a>
              <a href="#how" onClick={scrollToSection('how')} className="py-2">{t("how")}</a>
              <a href="#about" onClick={scrollToSection('about')} className="py-2">{t("about")}</a>
              <a href="#contact" onClick={scrollToSection('contact')} className="py-2">{t("contact")}</a>
              <div className="pt-2 border-t border-slate-100 flex gap-2">
                <Link href="/login" className="text-sm text-slate-700">{lang === "en" ? "Sign In" : "Kɔ mu"}</Link>
                <Link href="/register">
                  <Button size="sm" className="bg-gradient-to-r from-blue-600 to-teal-400 text-white">{t("cta_primary")}</Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Hero Card */}
        <header className="relative bg-white/80 backdrop-blur rounded-3xl shadow-2xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[68vh]">
          {/* Decorative blobs */}
          <div className="absolute -left-24 -top-16 w-72 h-72 rounded-full bg-gradient-to-tr from-blue-400 to-teal-300 blob opacity-80"></div>
          <div className="absolute -right-24 -bottom-20 w-80 h-80 rounded-full bg-gradient-to-br from-violet-300 to-blue-200 blob opacity-80"></div>

          <div className="relative z-10 lg:col-span-7 p-8 md:p-16 flex flex-col justify-center">
            <div className="text-sm text-blue-600 font-semibold uppercase tracking-wider mb-4">{t("tagline")}</div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 leading-tight mb-6">{t("heading")}</h1>
            <p className="text-slate-600 text-lg max-w-xl mb-8">{t("description")}</p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/register">
                <Button size="lg" className="px-8 py-4 bg-gradient-to-r from-blue-600 to-teal-400 hover:from-blue-700 text-white shadow-lg">{t("cta_primary")}</Button>
              </Link>

              <Button size="lg" variant="outline" className="px-8 py-4 border-slate-200" onClick={() => setLang(lang === "en" ? "ak" : "en")}>
                {lang === "en" ? t("cta_toggle") : "View in English"}
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-3 text-slate-500">
                <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center shadow-sm">
                  <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8 2 5 5 5 9c0 1.2.3 2.3.9 3.3C6.3 15.2 9 18 12 22c3-4 5.7-6.8 6.1-9.7.6-1 .9-2.1.9-3.3 0-4-3-7-7-7z"/></svg>
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-800">{t("access_title")}</div>
                  <div className="text-xs text-slate-500">{t("access_sub")}</div>
                </div>
              </div>

              <div className="flex items-center gap-3 text-slate-500">
                <div className="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center shadow-sm">
                  <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-800">{t("multilingual_title")}</div>
                  <div className="text-xs text-slate-500">{t("multilingual_sub")}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="relative z-10 lg:col-span-5 flex items-center justify-center p-6 md:p-12">
            {/* DNA Illustration - scalable SVG with subtle card */}
            <div className="max-w-md w-full dna-float rounded-2xl bg-white/60 p-6 shadow-xl">
              <svg viewBox="0 0 600 600" className="w-full h-auto" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <linearGradient id="g1" x1="0%" x2="100%" y1="0%" y2="100%">
                    <stop offset="0%" stopColor="#67b3ff" />
                    <stop offset="50%" stopColor="#9be7ff" />
                    <stop offset="100%" stopColor="#67b3ff" />
                  </linearGradient>
                </defs>
                <rect x="0" y="0" width="600" height="600" rx="20" fill="url(#g1)" opacity="0.06" />

                <g transform="translate(120,50)">
                  <path d="M60 0 C 20 70, 20 130, 60 200 C 100 270, 140 330, 180 400" stroke="#1e88e5" strokeWidth="12" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
                  <path d="M120 0 C 160 70, 160 130, 120 200 C 80 270, 40 330, 0 400" stroke="#60a5fa" strokeWidth="12" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
                  <g stroke="#ffffff" strokeWidth="6" opacity="0.95">
                    <path d="M30 50 L150 50" strokeOpacity="0.9"/>
                    <path d="M10 120 L170 120" strokeOpacity="0.9"/>
                    <path d="M30 190 L150 190" strokeOpacity="0.9"/>
                    <path d="M10 260 L170 260" strokeOpacity="0.9"/>
                    <path d="M30 330 L150 330" strokeOpacity="0.9"/>
                  </g>
                  <circle cx="30" cy="50" r="6" fill="#fff" opacity="0.95" />
                  <circle cx="150" cy="50" r="6" fill="#fff" opacity="0.95" />

                  <circle cx="10" cy="120" r="6" fill="#fff" opacity="0.95" />
                  <circle cx="170" cy="120" r="6" fill="#fff" opacity="0.95" />

                  <circle cx="30" cy="190" r="6" fill="#fff" opacity="0.95" />
                  <circle cx="150" cy="190" r="6" fill="#fff" opacity="0.95" />

                  <circle cx="10" cy="260" r="6" fill="#fff" opacity="0.95" />
                  <circle cx="170" cy="260" r="6" fill="#fff" opacity="0.95" />

                  <circle cx="30" cy="330" r="6" fill="#fff" opacity="0.95" />
                  <circle cx="150" cy="330" r="6" fill="#fff" opacity="0.95" />
                </g>

              </svg>
            </div>
          </div>
        </header>

        {/* Features Section */}
        <section id="features" className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">{t("features")}</h2>
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="p-6 rounded-xl shadow hover:shadow-lg transition transform hover:-translate-y-1 bg-gradient-to-br from-white to-slate-50">
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">{t("feature1_title")}</h3>
                <p className="text-sm text-slate-600">{t("feature1_desc")}</p>
              </div>

              <div className="p-6 rounded-xl shadow hover:shadow-lg transition transform hover:-translate-y-1 bg-gradient-to-br from-white to-slate-50">
                <div className="w-12 h-12 rounded-lg bg-emerald-50 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-emerald-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8 2 5 5 5 9c0 1.2.3 2.3.9 3.3C6.3 15.2 9 18 12 22c3-4 5.7-6.8 6.1-9.7.6-1 .9-2.1.9-3.3 0-4-3-7-7-7z"/></svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">{t("feature2_title")}</h3>
                <p className="text-sm text-slate-600">{t("feature2_desc")}</p>
              </div>

              <div className="p-6 rounded-xl shadow hover:shadow-lg transition transform hover:-translate-y-1 bg-gradient-to-br from-white to-slate-50">
                <div className="w-12 h-12 rounded-lg bg-pink-50 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-pink-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 6 3.5 4 6 4c1.7 0 3.1 1 3.9 2.4C11.9 5 13.3 4 15 4c2.5 0 4 2 4 4.5 0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">{t("feature3_title")}</h3>
                <p className="text-sm text-slate-600">{t("feature3_desc")}</p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how" className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-8">{t("how")}</h2>
            <div className="grid gap-6 sm:grid-cols-3">
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold mb-4">1</div>
                <h3 className="text-lg font-semibold mb-2">{t("how1_title")}</h3>
                <p className="text-sm text-slate-600">{t("how1_desc")}</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-teal-500 text-white font-bold mb-4">2</div>
                <h3 className="text-lg font-semibold mb-2">{t("how2_title")}</h3>
                <p className="text-sm text-slate-600">{t("how2_desc")}</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-600 text-white font-bold mb-4">3</div>
                <h3 className="text-lg font-semibold mb-2">{t("how3_title")}</h3>
                <p className="text-sm text-slate-600">{t("how3_desc")}</p>
              </div>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-6xl mx-auto grid gap-8 lg:grid-cols-2 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">{t("about_title")}</h2>
              <p className="text-slate-600 mb-4">{t("about_p1")}</p>
              <p className="text-slate-600">{t("about_p2")}</p>
            </div>
            <div className="flex items-center justify-center">
              {/* Simple illustrative SVG */}
              <svg className="w-full h-auto max-w-sm" viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
                <rect x="0" y="0" width="200" height="120" rx="8" fill="#eef6ff" />
                <circle cx="60" cy="60" r="26" fill="#67b3ff" />
                <rect x="100" y="30" width="70" height="60" rx="6" fill="#9be7ff" />
              </svg>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contact" className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-6">{t("contact_title")}</h2>
            <p className="text-center text-slate-600 mb-6">{t("contact_sub")}</p>

            <form className="grid gap-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <input aria-label="Name" placeholder={t("name_placeholder")} className="w-full rounded-lg border border-slate-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-200" />
                <input aria-label="Email" placeholder={t("email_placeholder")} className="w-full rounded-lg border border-slate-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-200" />
              </div>
              <textarea aria-label="Message" placeholder={t("message_placeholder")} rows={5} className="w-full rounded-lg border border-slate-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-200" />
              <div className="text-center">
                <button type="button" className="inline-flex items-center px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-teal-400 text-white shadow-md">{t("send_button")}</button>
              </div>
            </form>
          </div>
        </section>

        {/* Mobile quick CTA below hero */}
        <div className="mt-8 text-center md:hidden">
          <Link href="/register">
            <Button className="w-56 mx-auto bg-gradient-to-r from-blue-600 to-teal-400 text-white">{t("mobile_cta")}</Button>
          </Link>
        </div>

        {/* Footer */}
        <footer className="py-8 text-center text-sm text-slate-500">
          <div className="max-w-7xl mx-auto">© {new Date().getFullYear()} HEALTH — Built with care & privacy in mind.</div>
        </footer>
      </div>
    </div>
  )
}
