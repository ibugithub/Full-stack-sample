import Link from 'next/link';
import { ArrowRight, Database, LayoutDashboard, ShieldCheck, UserRound } from 'lucide-react';

const features = [
  {
    icon: ShieldCheck,
    title: 'Account access',
    text: 'Sign in, verify your email and manage your password.',
  },
  {
    icon: UserRound,
    title: 'Personal profiles',
    text: 'Keep your account details and personal information up to date.',
  },
  {
    icon: LayoutDashboard,
    title: 'Administration',
    text: 'Manage users, staff roles and access from one workspace.',
  },
  {
    icon: Database,
    title: 'Ready to extend',
    text: 'A clean foundation for the features your next project needs.',
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <section className="border-b border-blue-100 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
            Your next project starts here
          </p>
          <h1 className="mt-5 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
            A clear foundation.
            <br />
            <span className="text-blue-600">Room to build.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-gray-600">
            Accounts, profiles and a staff workspace, brought together in one application.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/accounts/signup"
              className="inline-flex min-h-12 items-center gap-2 rounded-lg bg-blue-600 px-5 font-semibold text-white hover:bg-blue-700"
            >
              Create account{' '}
              <ArrowRight
                size={18}
                aria-hidden="true"
              />
            </Link>
            <Link
              href="/accounts/signin"
              className="inline-flex min-h-12 items-center rounded-lg border border-gray-300 px-5 font-semibold hover:bg-gray-50"
            >
              Sign in
            </Link>
          </div>
        </div>
      </section>
      <section
        aria-label="Application features"
        className="mx-auto grid max-w-6xl gap-5 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4"
      >
        {features.map(({ icon: Icon, title, text }) => (
          <article
            key={title}
            className="rounded-2xl border border-gray-200 bg-white p-6"
          >
            <Icon
              size={24}
              aria-hidden="true"
              className="text-blue-600"
            />
            <h2 className="mt-5 text-lg font-semibold">{title}</h2>
            <p className="mt-3 text-sm leading-6 text-gray-600">{text}</p>
          </article>
        ))}
      </section>
      <footer className="mx-auto flex max-w-6xl flex-wrap justify-between gap-3 border-t border-gray-200 px-4 py-6 text-sm text-gray-500 sm:px-6">
        <span>Full-stack Template</span>
        <a
          href="/swagger/"
          className="hover:text-blue-700"
        >
          API documentation
        </a>
      </footer>
    </main>
  );
}
