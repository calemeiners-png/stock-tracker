import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://nxdjqmwbjmcfgcwzztdz.supabase.co";
const SUPABASE_ANON_KEY = "your_anon_key_here";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);