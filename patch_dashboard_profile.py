import os

filepath = "flask_replica/templates/dashboard.html"

with open(filepath, "r", encoding='utf-8') as f:
    lines = f.readlines()

profile_html = """
                <!-- Profile Panel -->
                <div id="panelProfile" class="hidden flex-1 flex flex-col space-y-4 overflow-y-auto custom-scrollbar">
                    <div class="bg-slate-800/50 p-5 rounded-xl border border-slate-700/50 space-y-4 max-w-lg bg-slate-900/40 mt-4">
                        <h3 class="font-semibold text-sm text-amber-500 flex items-center gap-1"><i data-lucide="user-cog" class="w-4 h-4"></i> Official Profile Settings</h3>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Qualifications</label>
                            <textarea id="profQuals" class="w-full h-20 bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-slate-100 resize-none" placeholder="e.g., LL.M, Chief Justice of Chamber..."></textarea>
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Experience</label>
                            <textarea id="profExp" class="w-full h-24 bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-slate-100 resize-none" placeholder="Years of Service, past cases..."></textarea>
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Landmark Judgements</label>
                            <textarea id="profCases" class="w-full h-24 bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-slate-100 resize-none" placeholder="Key cases decided..."></textarea>
                        </div>
                        <button onclick="saveProfile()" class="w-full bg-amber-600 hover:bg-amber-500 text-slate-900 font-bold p-2 rounded-lg text-sm transition-all flex items-center justify-center gap-1 shadow-md">
                            <i data-lucide="save" class="w-4 h-4"></i> Save Profile
                        </button>
                    </div>
                </div>
"""

found_idx = -1
for i, line in enumerate(lines):
    if "{% else %}" in line:
        found_idx = i
        break

if found_idx != -1:
    lines.insert(found_idx - 1, profile_html + "\n")
    with open(filepath, "w", encoding='utf-8') as f:
         f.writelines(lines)
    print("Patch for panelProfile applied successfully.")
else:
    print("Failed to find target anchor.")
