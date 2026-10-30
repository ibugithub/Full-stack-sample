interface User {
  admin_url?: string | null;
  is_staff?: boolean;
  name?: string;
  first_name?: string;
  last_name?: string;
  email: string;
  signup_method: 'email' | 'google' | 'facebook' | 'microsoft';
}
export interface ProfileInterface {
  admin_url?: string | null;
  is_staff?: boolean;
  first_name?: string;
  last_name?: string;
  email?: string;
  user: User;
  name: string;
  display_name: string | null;
  profile_picture: string | null;
  created_at: string;
  updated_at: string;
}
