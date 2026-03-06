<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Company Dashboard</h1>
      <p>Welcome, {{ companyName }}!</p>
    </div>

    <div v-if="successMsg" class="msg-box success-msg">{{ successMsg }}</div>
    <div v-if="errorMsg" class="msg-box error-msg">{{ errorMsg }}</div>

    <div class="stats-container">
      <div class="stat-card">
        <h3>Total Jobs</h3>
        <p class="stat-number">{{ stats.total_jobs }}</p>
      </div>
      <div class="stat-card">
        <h3>Active Jobs</h3>
        <p class="stat-number">{{ stats.active_jobs }}</p>
      </div>
      <div class="stat-card">
        <h3>Applications</h3>
        <p class="stat-number">{{ stats.total_applications }}</p>
      </div>
      <div class="stat-card">
        <h3>Shortlisted</h3>
        <p class="stat-number">{{ stats.shortlisted }}</p>
      </div>
      <div class="stat-card">
        <h3>Selected</h3>
        <p class="stat-number">{{ stats.selected }}</p>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'jobs' }" @click="activeTab = 'jobs'">My Jobs</button>
      <button :class="{ active: activeTab === 'postjob' }" @click="activeTab = 'postjob'">Post New Job</button>
      <button :class="{ active: activeTab === 'applicants' }" @click="activeTab = 'applicants'">View Applicants</button>
      <button :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">Company Profile</button>
    </div>

    <div class="tab-content">

      <div v-if="activeTab === 'jobs'">
        <h2>My Job Postings</h2>
        <div class="search-box">
          <input type="text" v-model="jobSearch" placeholder="Search jobs by title..." />
        </div>
        <table v-if="filteredJobs.length > 0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Location</th>
              <th>Salary</th>
              <th>Status</th>
              <th>Approved</th>
              <th>Applications</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in filteredJobs" :key="job.id">
              <td>{{ job.id }}</td>
              <td>{{ job.title }}</td>
              <td>{{ job.location }}</td>
              <td>{{ job.salary }}</td>
              <td>
                <span :class="job.status === 'Active' ? 'badge-green' : 'badge-red'">{{ job.status }}</span>
              </td>
              <td>
                <span :class="job.is_approved ? 'badge-green' : 'badge-yellow'">{{ job.is_approved ? 'Yes' : 'Pending' }}</span>
              </td>
              <td>{{ job.application_count }}</td>
              <td>
                <button class="btn-small btn-blue" @click="viewApplicants(job.id, job.title)">Applicants</button>
                <button class="btn-small" :class="job.status === 'Active' ? 'btn-red' : 'btn-green'" @click="toggleJobStatus(job.id)">
                  {{ job.status === 'Active' ? 'Close' : 'Reopen' }}
                </button>
                <button class="btn-small btn-yellow" @click="editJob(job)">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">No job postings found.</p>

        <div v-if="showEditModal" class="modal-overlay">
          <div class="modal">
            <h3>Edit Job</h3>
            <div class="form-group">
              <label>Title</label>
              <input type="text" v-model="editForm.title" />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>Location</label>
              <input type="text" v-model="editForm.location" />
            </div>
            <div class="form-group">
              <label>Salary</label>
              <input type="text" v-model="editForm.salary" />
            </div>
            <div class="form-group">
              <label>Skills Required</label>
              <input type="text" v-model="editForm.skills_required" />
            </div>
            <div class="form-group">
              <label>Experience Required</label>
              <input type="text" v-model="editForm.experience_required" />
            </div>
            <div class="form-group">
              <label>Benefits</label>
              <input type="text" v-model="editForm.benefits" />
            </div>
            <div class="form-group">
              <label>Last Date to Apply</label>
              <input type="date" v-model="editForm.last_date" />
            </div>
            <div class="modal-buttons">
              <button class="btn-green" @click="saveEditJob">Save</button>
              <button class="btn-red" @click="showEditModal = false">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'postjob'">
        <h2>Post New Job</h2>
        <div class="form-container">
          <div class="form-group">
            <label>Job Title *</label>
            <input type="text" v-model="newJob.title" placeholder="Enter job title" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newJob.description" rows="4" placeholder="Job description"></textarea>
          </div>
          <div class="form-group">
            <label>Location</label>
            <input type="text" v-model="newJob.location" placeholder="Job location" />
          </div>
          <div class="form-group">
            <label>Salary</label>
            <input type="text" v-model="newJob.salary" placeholder="e.g. 5-8 LPA" />
          </div>
          <div class="form-group">
            <label>Skills Required</label>
            <input type="text" v-model="newJob.skills_required" placeholder="e.g. Python, JavaScript, SQL" />
          </div>
          <div class="form-group">
            <label>Experience Required</label>
            <input type="text" v-model="newJob.experience_required" placeholder="e.g. 0-2 years" />
          </div>
          <div class="form-group">
            <label>Benefits</label>
            <input type="text" v-model="newJob.benefits" placeholder="e.g. Health Insurance, WFH" />
          </div>
          <div class="form-group">
            <label>Last Date to Apply</label>
            <input type="date" v-model="newJob.last_date" />
          </div>
          <button class="btn-submit" @click="postNewJob">Post Job</button>
        </div>
      </div>

      <div v-if="activeTab === 'applicants'">
        <h2>View Applicants</h2>
        <div class="form-group">
          <label>Select Job</label>
          <select v-model="selectedJobId" @change="loadApplicants">
            <option value="">-- Select a Job --</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.title }} ({{ job.status }})</option>
          </select>
        </div>

        <div v-if="selectedJobId && applicants.length > 0">
          <h3>Applicants for: {{ selectedJobTitle }}</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Education</th>
                <th>Skills</th>
                <th>Experience</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Feedback</th>
                <th>Interview</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applicants" :key="app.application_id">
                <td>{{ app.student_name }}</td>
                <td>{{ app.student_email }}</td>
                <td>{{ app.education }}</td>
                <td>{{ app.skills }}</td>
                <td>{{ app.experience }}</td>
                <td>{{ app.phone }}</td>
                <td>
                  <span :class="getStatusClass(app.status)">{{ app.status }}</span>
                </td>
                <td>{{ app.feedback || '-' }}</td>
                <td>
                  <span v-if="app.interview_date">{{ app.interview_date }} {{ app.interview_time }}<br/>{{ app.interview_location }}</span>
                  <span v-else>-</span>
                </td>
                <td>
                  <select v-model="app.newStatus" class="status-select">
                    <option value="">Change Status</option>
                    <option value="Shortlisted">Shortlist</option>
                    <option value="Interview">Interview</option>
                    <option value="Selected">Select</option>
                    <option value="Rejected">Reject</option>
                  </select>
                  <input type="text" v-model="app.newFeedback" placeholder="Feedback" class="feedback-input" />
                  <button class="btn-small btn-blue" @click="updateAppStatus(app)" :disabled="!app.newStatus">Update</button>
                  <button class="btn-small btn-yellow" @click="openInterviewModal(app)">Schedule Interview</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else-if="selectedJobId && applicants.length === 0" class="no-data">No applicants for this job.</p>
        <p v-else class="no-data">Select a job to view applicants.</p>

        <div v-if="showInterviewModal" class="modal-overlay">
          <div class="modal">
            <h3>Schedule Interview</h3>
            <p>Applicant: {{ interviewForm.student_name }}</p>
            <div class="form-group">
              <label>Interview Date</label>
              <input type="date" v-model="interviewForm.interview_date" />
            </div>
            <div class="form-group">
              <label>Interview Time</label>
              <input type="time" v-model="interviewForm.interview_time" />
            </div>
            <div class="form-group">
              <label>Interview Location</label>
              <input type="text" v-model="interviewForm.interview_location" placeholder="Location or Online Link" />
            </div>
            <div class="modal-buttons">
              <button class="btn-green" @click="scheduleInterview">Schedule</button>
              <button class="btn-red" @click="showInterviewModal = false">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'profile'">
        <h2>Company Profile</h2>
        <div class="form-container">
          <div class="profile-logo">
            <img src="https://via.placeholder.com/120x120?text=Logo" alt="Company Logo" />
          </div>
          <div class="form-group">
            <label>Company Name</label>
            <input type="text" v-model="profile.company_name" />
          </div>
          <div class="form-group">
            <label>Industry</label>
            <input type="text" v-model="profile.industry" />
          </div>
          <div class="form-group">
            <label>Location</label>
            <input type="text" v-model="profile.location" />
          </div>
          <div class="form-group">
            <label>Website</label>
            <input type="text" v-model="profile.website" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="profile.description" rows="4"></textarea>
          </div>
          <button class="btn-submit" @click="updateProfile">Update Profile</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDashboard',
  data() {
    return {
      companyName: '',
      activeTab: 'jobs',
      successMsg: '',
      errorMsg: '',
      stats: {
        total_jobs: 0,
        active_jobs: 0,
        total_applications: 0,
        shortlisted: 0,
        selected: 0
      },
      jobs: [],
      jobSearch: '',
      newJob: {
        title: '',
        description: '',
        location: '',
        salary: '',
        skills_required: '',
        experience_required: '',
        benefits: '',
        last_date: ''
      },
      showEditModal: false,
      editForm: {
        id: null,
        title: '',
        description: '',
        location: '',
        salary: '',
        skills_required: '',
        experience_required: '',
        benefits: '',
        last_date: ''
      },
      selectedJobId: '',
      selectedJobTitle: '',
      applicants: [],
      showInterviewModal: false,
      interviewForm: {
        application_id: null,
        student_name: '',
        interview_date: '',
        interview_time: '',
        interview_location: ''
      },
      profile: {
        company_name: '',
        industry: '',
        location: '',
        website: '',
        description: ''
      }
    }
  },
  computed: {
    filteredJobs() {
      if (!this.jobSearch) return this.jobs
      var search = this.jobSearch.toLowerCase()
      return this.jobs.filter(function(j) {
        return j.title.toLowerCase().includes(search)
      })
    }
  },
  mounted() {
    this.loadCompanyInfo()
    this.loadStats()
    this.loadJobs()
    this.loadProfile()
  },
  methods: {
    showSuccess(msg) {
      this.successMsg = msg
      this.errorMsg = ''
      var self = this
      setTimeout(function() { self.successMsg = '' }, 3000)
    },
    showError(msg) {
      this.errorMsg = msg
      this.successMsg = ''
      var self = this
      setTimeout(function() { self.errorMsg = '' }, 3000)
    },
    getToken() {
      return localStorage.getItem('token')
    },
    getStatusClass(status) {
      if (status === 'Applied') return 'badge-blue'
      if (status === 'Shortlisted') return 'badge-yellow'
      if (status === 'Interview') return 'badge-purple'
      if (status === 'Selected') return 'badge-green'
      if (status === 'Rejected') return 'badge-red'
      return ''
    },
    async loadCompanyInfo() {
      try {
        var response = await fetch('http://localhost:5000/api/current_user', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.companyName = data.company_name || 'Company'
        }
      } catch (error) {
        this.companyName = 'Company'
      }
    },
    async loadStats() {
      try {
        var response = await fetch('http://localhost:5000/api/company/stats', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.stats = data
        }
      } catch (error) {
        console.log(error)
      }
    },
    async loadJobs() {
      try {
        var response = await fetch('http://localhost:5000/api/company/jobs', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.jobs = data
        }
      } catch (error) {
        console.log(error)
      }
    },
    async postNewJob() {
      if (!this.newJob.title) {
        this.showError('Job title is required')
        return
      }
      try {
        var response = await fetch('http://localhost:5000/api/company/jobs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.getToken()
          },
          body: JSON.stringify(this.newJob)
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.newJob = { title: '', description: '', location: '', salary: '', skills_required: '', experience_required: '', benefits: '', last_date: '' }
          this.loadJobs()
          this.loadStats()
          this.activeTab = 'jobs'
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to post job')
      }
    },
    async toggleJobStatus(jobId) {
      try {
        var response = await fetch('http://localhost:5000/api/company/jobs/' + jobId + '/close', {
          method: 'PUT',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadJobs()
          this.loadStats()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to update job status')
      }
    },
    editJob(job) {
      this.editForm = {
        id: job.id,
        title: job.title,
        description: job.description,
        location: job.location,
        salary: job.salary,
        skills_required: job.skills_required,
        experience_required: job.experience_required,
        benefits: job.benefits,
        last_date: job.last_date
      }
      this.showEditModal = true
    },
    async saveEditJob() {
      try {
        var response = await fetch('http://localhost:5000/api/company/jobs/' + this.editForm.id, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.getToken()
          },
          body: JSON.stringify(this.editForm)
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.showEditModal = false
          this.loadJobs()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to update job')
      }
    },
    viewApplicants(jobId, jobTitle) {
      this.selectedJobId = jobId
      this.selectedJobTitle = jobTitle
      this.activeTab = 'applicants'
      this.loadApplicants()
    },
    async loadApplicants() {
      if (!this.selectedJobId) {
        this.applicants = []
        return
      }
      var job = this.jobs.find(function(j) { return j.id == this.selectedJobId }.bind(this))
      if (job) this.selectedJobTitle = job.title
      try {
        var response = await fetch('http://localhost:5000/api/company/jobs/' + this.selectedJobId + '/applicants', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.applicants = data.map(function(a) {
            a.newStatus = ''
            a.newFeedback = ''
            return a
          })
        }
      } catch (error) {
        console.log(error)
      }
    },
    async updateAppStatus(app) {
      if (!app.newStatus) return
      try {
        var response = await fetch('http://localhost:5000/api/company/applications/' + app.application_id + '/status', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.getToken()
          },
          body: JSON.stringify({ status: app.newStatus, feedback: app.newFeedback })
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadApplicants()
          this.loadStats()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to update status')
      }
    },
    openInterviewModal(app) {
      this.interviewForm = {
        application_id: app.application_id,
        student_name: app.student_name,
        interview_date: app.interview_date || '',
        interview_time: app.interview_time || '',
        interview_location: app.interview_location || ''
      }
      this.showInterviewModal = true
    },
    async scheduleInterview() {
      if (!this.interviewForm.interview_date) {
        this.showError('Interview date is required')
        return
      }
      try {
        var response = await fetch('http://localhost:5000/api/company/applications/' + this.interviewForm.application_id + '/interview', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.getToken()
          },
          body: JSON.stringify({
            interview_date: this.interviewForm.interview_date,
            interview_time: this.interviewForm.interview_time,
            interview_location: this.interviewForm.interview_location
          })
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.showInterviewModal = false
          this.loadApplicants()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to schedule interview')
      }
    },
    async loadProfile() {
      try {
        var response = await fetch('http://localhost:5000/api/company/profile', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.profile.company_name = data.company_name || ''
          this.profile.industry = data.industry || ''
          this.profile.location = data.location || ''
          this.profile.website = data.website || ''
          this.profile.description = data.description || ''
        }
      } catch (error) {
        console.log(error)
      }
    },
    async updateProfile() {
      try {
        var response = await fetch('http://localhost:5000/api/company/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': this.getToken()
          },
          body: JSON.stringify(this.profile)
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadCompanyInfo()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Failed to update profile')
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 20px;
}

.dashboard-header h1 {
  color: #2c3e50;
  font-size: 28px;
}

.dashboard-header p {
  color: #7f8c8d;
  font-size: 16px;
  margin-top: 5px;
}

.msg-box {
  padding: 12px 20px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 14px;
}

.success-msg {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error-msg {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.stats-container {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  min-width: 150px;
  text-align: center;
}

.stat-card h3 {
  color: #7f8c8d;
  font-size: 13px;
  margin-bottom: 8px;
}

.stat-number {
  color: #2c3e50;
  font-size: 32px;
  font-weight: bold;
}

.tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
  border-radius: 6px 6px 0 0;
  color: #555;
}

.tabs button.active {
  background: #3498db;
  color: white;
}

.tabs button:hover {
  background: #ddd;
}

.tabs button.active:hover {
  background: #2980b9;
}

.tab-content {
  background: white;
  padding: 25px;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-content h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 22px;
}

.search-box {
  margin-bottom: 15px;
}

.search-box input {
  width: 300px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead {
  background: #f8f9fa;
}

th, td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: 600;
  color: #555;
}

.badge-green {
  background: #d4edda;
  color: #155724;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.badge-red {
  background: #f8d7da;
  color: #721c24;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.badge-yellow {
  background: #fff3cd;
  color: #856404;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.badge-blue {
  background: #d1ecf1;
  color: #0c5460;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.badge-purple {
  background: #e2d5f1;
  color: #5b2c8e;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.btn-small {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin: 2px;
  color: white;
}

.btn-blue {
  background: #3498db;
}

.btn-red {
  background: #e74c3c;
}

.btn-green {
  background: #27ae60;
}

.btn-yellow {
  background: #f39c12;
}

.btn-blue:hover { background: #2980b9; }
.btn-red:hover { background: #c0392b; }
.btn-green:hover { background: #219a52; }
.btn-yellow:hover { background: #d68910; }

.no-data {
  color: #999;
  text-align: center;
  padding: 30px;
  font-size: 14px;
}

.form-container {
  max-width: 600px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
  font-size: 14px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.btn-submit {
  background: #3498db;
  color: white;
  padding: 10px 30px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
}

.btn-submit:hover {
  background: #2980b9;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.modal-buttons button {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: white;
}

.status-select {
  padding: 4px;
  font-size: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 2px;
}

.feedback-input {
  padding: 4px;
  font-size: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100px;
  margin: 2px;
}

.profile-logo {
  text-align: center;
  margin-bottom: 20px;
}

.profile-logo img {
  width: 120px;
  height: 120px;
  border-radius: 10px;
  border: 2px solid #ddd;
}
</style>
