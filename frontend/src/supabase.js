import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "your_project_url_here";
const SUPABASE_ANON_KEY = "your_anon_key_here";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);