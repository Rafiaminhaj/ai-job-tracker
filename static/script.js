// Frontend Logic for AI Job Application Tracker

document.addEventListener("DOMContentLoaded", () => {
    // Load initial jobs
    fetchJobs();

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
        
        // Match tag color based on status
        let statusClass = job.status.toLowerCase();
        
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

    // Activate selected
    if (tabName === "analyzer") {
        document.querySelector("[onclick=\"switchTab('analyzer')\"]").classList.add("active");
        document.getElementById("tab-analyzer").classList.add("active");
    } else {
        document.querySelector("[onclick=\"switchTab('drafter')\"]").classList.add("active");
        document.getElementById("tab-drafter").classList.add("active");
    }
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

    analysis.matching_skills.forEach(skill => {
        const tag = document.createElement("span");
        tag.className = "tag match";
        tag.textContent = skill;
        matchingContainer.appendChild(tag);
    });

    analysis.missing_skills.forEach(skill => {
        const tag = document.createElement("span");
        tag.className = "tag missing";
        tag.textContent = skill;
        missingContainer.appendChild(tag);
    });

    // Tips rendering
    const tipsList = document.getElementById("tips-list");
    tipsList.innerHTML = "";
    analysis.tips.forEach(tip => {
        const li = document.createElement("li");
        li.textContent = tip;
        tipsList.appendChild(li);
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
