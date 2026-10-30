type Provider = 'Google' | 'Facebook' | 'Microsoft';

export function beginOAuth(provider: Provider, url: string) {
  const state = crypto.randomUUID();
  sessionStorage.setItem(`oauth-state-${provider}`, state);
  const destination = new URL(url);
  destination.searchParams.set('state', state);
  window.location.assign(destination.toString());
}

export function consumeOAuthState(provider: Provider, state: string | null) {
  const key = `oauth-state-${provider}`;
  const expected = sessionStorage.getItem(key);
  sessionStorage.removeItem(key);
  return !!expected && state === expected;
}
