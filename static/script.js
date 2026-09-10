// Frontend Logic for AI Job Application Tracker

let currentVisionData = null;

document.addEventListener("DOMContentLoaded", () => {
    // Load initial jobs
    fetchJobs();

    // Tab buttons event listener binding for 100% reliability
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const tabName = btn.getAttribute("data-tab");
            if (tabName) {
                switchTab(tabName);
            }
        });
    });

    // Event Listeners for Modal
    const openModalBtn = document.getElementById("open-modal-btn");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const jobModal = document.getElementById("job-modal");
    const addJobForm = document.getElementById("add-job-form");

    openModalBtn.addEventListener("click", () => {
        jobModal.classList.add("active");
    });

    closeModalBtn.addEventListener("click", () => {
        jobModal.classList.remove("active");
    });

    // Close modal when clicking outside the card
    window.addEventListener("click", (e) => {
        if (e.target === jobModal) {
            jobModal.classList.remove("active");
        }
    });

    // Add Job Form Submit
    addJobForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const jobData = {
            title: document.getElementById("job-title").value,
            company: document.getElementById("job-company").value,
            status: document.getElementById("job-status").value,
            url: document.getElementById("job-url").value,
            description: document.getElementById("job-description").value,
            notes: document.getElementById("job-notes").value
        };

        try {
            const response = await fetch("/api/jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jobData)
            });

            if (response.ok) {
                showToast("Job application saved to Cloud Firestore!", "success");
                addJobForm.reset();
                jobModal.classList.remove("active");
                fetchJobs(); // Refresh the list
            } else {
                showToast("Failed to save job application.", "error");
            }
        } catch (error) {
            console.error("Error saving job:", error);
            showToast("Server error. Check local console.", "error");
        }
    });

    // Resume Analyzer API call
    const analyzeBtn = document.getElementById("analyze-btn");
    analyzeBtn.addEventListener("click", async () => {
        const jd = document.getElementById("jd-text").value.trim();
        const resume = document.getElementById("resume-text").value.trim();

        if (!jd) {
            showToast("Please paste a Job Description first!", "error");
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = `Analyzing... <i class="fa-solid fa-spinner fa-spin"></i>`;

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_description: jd,
                    resume_text: resume ? resume : null
                })
            });

            if (response.ok) {
                const data = await response.json();
                renderAnalysis(data.analysis);
                showToast("Gemini Analysis Completed!", "success");
            } else {
                showToast("AI analysis failed.", "error");
            }
        } catch (error) {
            console.error("Error analyzing:", error);
            showToast("Server error during AI analysis.", "error");
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = `Analyze with Gemini <i class="fa-solid fa-brain"></i>`;
        }
    });

    // Email Drafter API call
    const draftBtn = document.getElementById("draft-btn");
    draftBtn.addEventListener("click", async () => {
        const title = document.getElementById("email-job").value.trim();
        const company = document.getElementById("email-company").value.trim();
        const stage = document.getElementById("email-stage").value;
        const context = document.getElementById("email-context").value.trim();

        if (!title || !company) {
            showToast("Please fill out Job Title and Company fields!", "error");
            return;
        }

        draftBtn.disabled = true;
        draftBtn.innerHTML = `Writing... <i class="fa-solid fa-spinner fa-spin"></i>`;

        try {
            const response = await fetch("/api/draft-email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_title: title,
                    company: company,
                    stage: stage,
                    context: context
                })
            });

            if (response.ok) {
                const data = await response.json();
                const outputPanel = document.getElementById("email-output-panel");
                const contentBox = document.getElementById("email-content-box");
                
                contentBox.textContent = data.draft;
                outputPanel.style.display = "block";
                showToast("Email Draft Generated!", "success");
            } else {
                showToast("AI drafting failed.", "error");
            }
        } catch (error) {
            console.error("Error drafting email:", error);
            showToast("Server error during AI drafting.", "error");
        } finally {
            draftBtn.disabled = false;
            draftBtn.innerHTML = `Generate Draft with Gemini <i class="fa-solid fa-bolt"></i>`;
        }
    });

    // Astra Vision Poster Scanner Logic
    const dropzone = document.getElementById("poster-dropzone");
    const fileInput = document.getElementById("poster-file-input");
    const filePreviewInfo = document.getElementById("file-preview-info");
    const scanPosterBtn = document.getElementById("scan-poster-btn");
    const autofillJobBtn = document.getElementById("autofill-job-btn");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                filePreviewInfo.style.display = "block";
                filePreviewInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            }
        });

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("dragover");
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                const file = fileInput.files[0];
                filePreviewInfo.style.display = "block";
                filePreviewInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            }
        });
    }

    if (scanPosterBtn) {
        scanPosterBtn.addEventListener("click", async () => {
            const file = fileInput ? fileInput.files[0] : null;

            scanPosterBtn.disabled = true;
            scanPosterBtn.innerHTML = `Scanning with Gemini Vision... <i class="fa-solid fa-spinner fa-spin"></i>`;

            try {
                const formData = new FormData();
                if (file) {
                    formData.append("file", file);
                } else {
                    // Create a dummy image blob for demo scan if no file is selected
                    const canvas = document.createElement("canvas");
                    canvas.width = 100;
                    canvas.height = 100;
                    const ctx = canvas.getContext("2d");
                    ctx.fillStyle = "#3b82f6";
                    ctx.fillRect(0, 0, 100, 100);
                    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
                    formData.append("file", blob, "demo_poster.jpg");
                }

                const response = await fetch("/api/scan-poster", {
                    method: "POST",
                    body: formData
                });

                if (response.ok) {
                    const resData = await response.json();
                    currentVisionData = resData.data;
                    renderVisionResult(currentVisionData);
                    showToast("Astra Vision Extraction Complete!", "success");
                } else {
                    showToast("Failed to scan poster with Gemini Vision.", "error");
                }
            } catch (error) {
                console.error("Error scanning poster:", error);
                showToast("Server error during Vision AI scan.", "error");
            } finally {
                scanPosterBtn.disabled = false;
                scanPosterBtn.innerHTML = `Scan Poster with Astra Vision AI <i class="fa-solid fa-wand-magic-sparkles"></i>`;
            }
        });
    }

    if (autofillJobBtn) {
        autofillJobBtn.addEventListener("click", () => {
            if (!currentVisionData) return;

            document.getElementById("job-title").value = currentVisionData.title || "";
            document.getElementById("job-company").value = currentVisionData.company || "";
            document.getElementById("job-description").value = currentVisionData.description || "";
            document.getElementById("job-notes").value = currentVisionData.notes || "Scanned via Astra Vision AI";

            jobModal.classList.add("active");
            showToast("Job details auto-filled in application form!", "success");
        });
    }

    // Launch Autonomous Auto-Apply AI Agent Logic
    const launchAgentBtn = document.getElementById("launch-agent-btn");
    if (launchAgentBtn) {
        launchAgentBtn.addEventListener("click", async () => {
            const company = document.getElementById("autoapply-company").value.trim();
            const url = document.getElementById("autoapply-url").value.trim();
            const hrEmail = document.getElementById("autoapply-hremail").value.trim();

            if (!company || !url) {
                showToast("Please enter Company Name and Target Job URL!", "error");
                return;
            }

            launchAgentBtn.disabled = true;
            launchAgentBtn.innerHTML = `Running Autonomous Agent... <i class="fa-solid fa-spinner fa-spin"></i>`;

            try {
                const response = await fetch("/api/auto-apply", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        company: company,
                        job_url: url,
                        hr_email: hrEmail ? hrEmail : null
                    })
                });

                if (response.ok) {
                    const resData = await response.json();
                    renderAgentLog(resData.agent_result);
                    showToast(`Autonomous AI Agent Applied to ${company}!`, "success");
                    fetchJobs(); // Refresh dashboard jobs list
                } else {
                    showToast("AI Agent execution failed.", "error");
                }
            } catch (error) {
                console.error("Error running AI Agent:", error);
                showToast("Server error running Auto-Apply Agent.", "error");
            } finally {
                launchAgentBtn.disabled = false;
                launchAgentBtn.innerHTML = `Launch Auto-Apply AI Agent <i class="fa-solid fa-rocket"></i>`;
            }
        });
    }

    // Copy to clipboard feature
    const copyBtn = document.getElementById("copy-email-btn");
    copyBtn.addEventListener("click", () => {
        const contentBox = document.getElementById("email-content-box");
        navigator.clipboard.writeText(contentBox.textContent);
        showToast("Copied to clipboard!", "success");
    });
});

// Fetch all jobs and render
async function fetchJobs() {
    try {
        const response = await fetch("/api/jobs");
        if (response.ok) {
            const jobs = await response.json();
            renderJobs(jobs);
            updateStats(jobs);
        }
    } catch (error) {
        console.error("Error fetching jobs:", error);
    }
}

// Render Job List
function renderJobs(jobs) {
    const listContainer = document.getElementById("job-list");
    listContainer.innerHTML = "";

    if (jobs.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-folder-open empty-icon"></i>
                <p>No job applications logged yet. Click 'Add Application' to get started!</p>
            </div>
        `;
        return;
    }

    // Sort jobs: latest date first
    jobs.sort((a, b) => new Date(b.date_applied) - new Date(a.date_applied));

    jobs.forEach(job => {
        const card = document.createElement("div");
        card.className = "job-card glass scroll-reveal";
        
        card.innerHTML = `
            <div class="job-info-block">
                <div class="job-title-wrapper">
                    <h4>${job.title}</h4>
                    <span class="company-tag"><i class="fa-solid fa-building"></i> ${job.company}</span>
                </div>
                <div class="job-meta">
                    <span><i class="fa-solid fa-calendar-days"></i> Applied: ${job.date_applied}</span>
                    ${job.url ? `<a href="${job.url}" target="_blank"><i class="fa-solid fa-arrow-up-right-from-square"></i> Post Link</a>` : ""}
                    ${job.notes ? `<span><i class="fa-solid fa-clipboard-question"></i> ${job.notes}</span>` : ""}
                </div>
            </div>
            <div class="job-actions-block">
                <select class="status-select" onchange="updateJobStatus('${job.id}', this.value)">
                    <option value="Applied" ${job.status === "Applied" ? "selected" : ""}>Applied</option>
                    <option value="Interviewing" ${job.status === "Interviewing" ? "selected" : ""}>Interviewing</option>
                    <option value="Offered" ${job.status === "Offered" ? "selected" : ""}>Offered</option>
                    <option value="Rejected" ${job.status === "Rejected" ? "selected" : ""}>Rejected</option>
                </select>
                <button class="btn-delete" onclick="deleteJob('${job.id}')" title="Delete Log">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

// Update Dashboard Counter statistics
function updateStats(jobs) {
    const counts = { Applied: 0, Interviewing: 0, Offered: 0, Rejected: 0 };
    jobs.forEach(job => {
        if (counts.hasOwnProperty(job.status)) {
            counts[job.status]++;
        }
    });

    document.getElementById("stat-applied").textContent = counts.Applied;
    document.getElementById("stat-interviewing").textContent = counts.Interviewing;
    document.getElementById("stat-offered").textContent = counts.Offered;
    document.getElementById("stat-rejected").textContent = counts.Rejected;
}

// Update job status API
async function updateJobStatus(id, newStatus) {
    try {
        const response = await fetch(`/api/jobs/${id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });
        if (response.ok) {
            showToast("Status updated successfully!", "success");
            fetchJobs();
        } else {
            showToast("Failed to update status.", "error");
        }
    } catch (error) {
        console.error("Error updating status:", error);
    }
}

// Delete job API
async function deleteJob(id) {
    if (!confirm("Are you sure you want to delete this job application log?")) return;

    try {
        const response = await fetch(`/api/jobs/${id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            showToast("Application deleted.", "success");
            fetchJobs();
        } else {
            showToast("Failed to delete application.", "error");
        }
    } catch (error) {
        console.error("Error deleting job:", error);
    }
}

// Tab Switch Logic
function switchTab(tabName) {
    // Deactivate all tabs
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));

    // Activate selected tab content
    const targetContent = document.getElementById(`tab-${tabName}`);
    if (targetContent) {
        targetContent.classList.add("active");
    }

    // Activate matching button
    const targetBtn = document.querySelector(`[data-tab="${tabName}"]`) || document.querySelector(`[onclick*="${tabName}"]`);
    if (targetBtn) {
        targetBtn.classList.add("active");
    }
}
window.switchTab = switchTab;

// Render Agent execution step logs
function renderAgentLog(result) {
    const panel = document.getElementById("agent-result-panel");
    const list = document.getElementById("agent-steps-list");
    panel.style.display = "block";
    list.innerHTML = "";

    (result.steps_completed || []).forEach(step => {
        const item = document.createElement("li");
        item.style.fontSize = "13px";
        item.style.color = "var(--text-primary)";
        item.style.background = "rgba(255, 255, 255, 0.03)";
        item.style.border = "1px solid var(--card-border)";
        item.style.padding = "10px 14px";
        item.style.borderRadius = "8px";
        item.style.display = "flex";
        item.style.alignItems = "center";
        item.style.gap = "10px";
        item.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #38bdf8;"></i> <span>${step}</span>`;
        list.appendChild(item);
    });
}

// Render Resume analysis results
function renderAnalysis(analysis) {
    const resultPanel = document.getElementById("analysis-result-panel");
    resultPanel.style.display = "block";

    // Set score text
    const scoreVal = analysis.match_score || 0;
    document.getElementById("score-text").textContent = `${scoreVal}%`;

    // Animate circular progress ring
    const circle = document.getElementById("progress-circle");
    const radius = circle.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (scoreVal / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    // Skills rendering
    const matchingContainer = document.getElementById("matching-tags");
    const missingContainer = document.getElementById("missing-tags");
    
    matchingContainer.innerHTML = "";
    missingContainer.innerHTML = "";

    (analysis.matching_skills || []).forEach(skill => {
        const tag = document.createElement("span");
        tag.className = "tag match";
        tag.textContent = skill;
        matchingContainer.appendChild(tag);
    });

    (analysis.missing_skills || []).forEach(skill => {
        const tag = document.createElement("span");
        tag.className = "tag missing";
        tag.textContent = skill;
        missingContainer.appendChild(tag);
    });

    // Tips rendering
    const tipsList = document.getElementById("tips-list");
    tipsList.innerHTML = "";
    (analysis.tips || []).forEach(tip => {
        const li = document.createElement("li");
        li.textContent = tip;
        tipsList.appendChild(li);
    });
}

// Render Astra Vision AI results
function renderVisionResult(data) {
    const panel = document.getElementById("vision-result-panel");
    panel.style.display = "block";

    document.getElementById("vision-title").textContent = data.title || "Not identified";
    document.getElementById("vision-company").textContent = data.company || "Not identified";
    document.getElementById("vision-salary").textContent = data.salary_range || "Not specified";
    document.getElementById("vision-description").value = data.description || "";

    const skillsContainer = document.getElementById("vision-skills-tags");
    skillsContainer.innerHTML = "";
    (data.required_skills || []).forEach(skill => {
        const tag = document.createElement("span");
        tag.className = "tag match";
        tag.style.borderColor = "rgba(168, 85, 247, 0.4)";
        tag.style.color = "#a855f7";
        tag.style.background = "rgba(168, 85, 247, 0.1)";
        tag.textContent = skill;
        skillsContainer.appendChild(tag);
    });
}

// Custom Toast alert system
function showToast(message, type) {
    const container = document.getElementById("notification-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = type === "success" ? "fa-circle-check" : "fa-circle-exclamation";
    let iconColor = type === "success" ? "var(--success-color)" : "var(--danger-color)";
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}" style="color: ${iconColor}; font-size: 16px;"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    // Fade out and remove toast after 3.5s
    setTimeout(() => {
        toast.style.animation = "slideIn 0.3s reverse forwards";
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3500);
}

