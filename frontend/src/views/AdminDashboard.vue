<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <p>Welcome, Admin!</p>
    </div>

    <div class="stats-container">
      <div class="stat-card">
        <h3>Total Students</h3>
        <p class="stat-number">{{ stats.total_students }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Companies</h3>
        <p class="stat-number">{{ stats.total_companies }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Jobs</h3>
        <p class="stat-number">{{ stats.total_jobs }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Applications</h3>
        <p class="stat-number">{{ stats.total_applications }}</p>
      </div>
      <div class="stat-card stat-pending">
        <h3>Pending Companies</h3>
        <p class="stat-number">{{ stats.pending_companies }}</p>
      </div>
      <div class="stat-card stat-pending">
        <h3>Pending Jobs</h3>
        <p class="stat-number">{{ stats.pending_jobs }}</p>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'companies' }" @click="activeTab = 'companies'">Companies</button>
      <button :class="{ active: activeTab === 'students' }" @click="activeTab = 'students'">Students</button>
      <button :class="{ active: activeTab === 'jobs' }" @click="activeTab = 'jobs'">Job Postings</button>
      <button :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">Applications</button>
    </div>

    <div class="tab-content" v-if="activeTab === 'companies'">
      <div class="section-header">
        <h2>Manage Companies</h2>
        <div class="search-box">
          <input type="text" v-model="companySearch" placeholder="Search by name or industry..." @input="searchCompanies" />
        </div>
      </div>

      <div class="message-box success" v-if="successMsg">{{ successMsg }}</div>
      <div class="message-box error" v-if="errorMsg">{{ errorMsg }}</div>

      <table class="data-table" v-if="companies.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Company Name</th>
            <th>Email</th>
            <th>Industry</th>
            <th>Location</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in companies" :key="company.id">
            <td>{{ company.id }}</td>
            <td>{{ company.company_name }}</td>
            <td>{{ company.email }}</td>
            <td>{{ company.industry || '-' }}</td>
            <td>{{ company.location || '-' }}</td>
            <td>
              <span class="badge approved" v-if="company.is_approved && !company.is_blacklisted">Approved</span>
              <span class="badge pending" v-if="!company.is_approved && !company.is_blacklisted">Pending</span>
              <span class="badge blacklisted" v-if="company.is_blacklisted">Blacklisted</span>
            </td>
            <td class="actions">
              <button class="btn-approve" v-if="!company.is_approved" @click="approveCompany(company.id)">Approve</button>
              <button class="btn-blacklist" @click="blacklistCompany(company.id)">
                {{ company.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
              </button>
              <button class="btn-remove" @click="removeCompany(company.id)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p class="no-data" v-else>No companies found.</p>
    </div>

    <div class="tab-content" v-if="activeTab === 'students'">
      <div class="section-header">
        <h2>Manage Students</h2>
        <div class="search-box">
          <input type="text" v-model="studentSearch" placeholder="Search by name, ID or contact..." @input="searchStudents" />
        </div>
      </div>

      <div class="message-box success" v-if="successMsg">{{ successMsg }}</div>
      <div class="message-box error" v-if="errorMsg">{{ errorMsg }}</div>

      <table class="data-table" v-if="students.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Email</th>
            <th>Roll Number</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td>{{ student.id }}</td>
            <td>{{ student.full_name }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.roll_number || '-' }}</td>
            <td>{{ student.phone || '-' }}</td>
            <td>
              <span class="badge approved" v-if="!student.is_blacklisted">Active</span>
              <span class="badge blacklisted" v-if="student.is_blacklisted">Blacklisted</span>
            </td>
            <td class="actions">
              <button class="btn-blacklist" @click="blacklistStudent(student.id)">
                {{ student.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
              </button>
              <button class="btn-remove" @click="removeStudent(student.id)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p class="no-data" v-else>No students found.</p>
    </div>

    <div class="tab-content" v-if="activeTab === 'jobs'">
      <div class="section-header">
        <h2>Manage Job Postings</h2>
      </div>

      <div class="message-box success" v-if="successMsg">{{ successMsg }}</div>
      <div class="message-box error" v-if="errorMsg">{{ errorMsg }}</div>

      <table class="data-table" v-if="jobs.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Salary</th>
            <th>Applications</th>
            <th>Status</th>
            <th>Approved</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>{{ job.id }}</td>
            <td>{{ job.title }}</td>
            <td>{{ job.company_name }}</td>
            <td>{{ job.location || '-' }}</td>
            <td>{{ job.salary || '-' }}</td>
            <td>{{ job.application_count }}</td>
            <td>
              <span class="badge approved" v-if="job.status === 'Active'">Active</span>
              <span class="badge pending" v-if="job.status === 'Closed'">Closed</span>
            </td>
            <td>
              <span class="badge approved" v-if="job.is_approved">Yes</span>
              <span class="badge pending" v-if="!job.is_approved">No</span>
            </td>
            <td class="actions">
              <button class="btn-approve" v-if="!job.is_approved" @click="approveJob(job.id)">Approve</button>
              <button class="btn-remove" @click="removeJob(job.id)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p class="no-data" v-else>No job postings found.</p>
    </div>

    <div class="tab-content" v-if="activeTab === 'applications'">
      <div class="section-header">
        <h2>All Applications</h2>
      </div>

      <table class="data-table" v-if="applications.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Student Name</th>
            <th>Student Email</th>
            <th>Job Title</th>
            <th>Company</th>
            <th>Status</th>
            <th>Applied Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications" :key="app.id">
            <td>{{ app.id }}</td>
            <td>{{ app.student_name }}</td>
            <td>{{ app.student_email }}</td>
            <td>{{ app.job_title }}</td>
            <td>{{ app.company_name }}</td>
            <td>
              <span class="badge" :class="getStatusClass(app.status)">{{ app.status }}</span>
            </td>
            <td>{{ app.applied_date }}</td>
          </tr>
        </tbody>
      </table>
      <p class="no-data" v-else>No applications found.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      activeTab: 'companies',
      stats: {
        total_students: 0,
        total_companies: 0,
        total_jobs: 0,
        total_applications: 0,
        total_placements: 0,
        pending_companies: 0,
        pending_jobs: 0
      },
      companies: [],
      students: [],
      jobs: [],
      applications: [],
      companySearch: '',
      studentSearch: '',
      successMsg: '',
      errorMsg: ''
    }
  },
  mounted() {
    this.loadStats()
    this.loadCompanies()
    this.loadStudents()
    this.loadJobs()
    this.loadApplications()
  },
  methods: {
    getToken() {
      return localStorage.getItem('token')
    },

    clearMessages() {
      this.successMsg = ''
      this.errorMsg = ''
    },

    showSuccess(msg) {
      this.successMsg = msg
      this.errorMsg = ''
      setTimeout(() => { this.successMsg = '' }, 3000)
    },

    showError(msg) {
      this.errorMsg = msg
      this.successMsg = ''
      setTimeout(() => { this.errorMsg = '' }, 3000)
    },

    getStatusClass(status) {
      if (status === 'Applied') return 'pending'
      if (status === 'Shortlisted') return 'approved'
      if (status === 'Selected' || status === 'Placed') return 'approved'
      if (status === 'Rejected') return 'blacklisted'
      return 'pending'
    },

    async loadStats() {
      try {
        var response = await fetch('http://localhost:5000/api/admin/stats', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.stats = data
        }
      } catch (error) {
        console.log('Error loading stats')
      }
    },

    async loadCompanies() {
      try {
        var url = 'http://localhost:5000/api/admin/companies'
        if (this.companySearch) {
          url = url + '?search=' + this.companySearch
        }
        var response = await fetch(url, {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.companies = data
        }
      } catch (error) {
        console.log('Error loading companies')
      }
    },

    async loadStudents() {
      try {
        var url = 'http://localhost:5000/api/admin/students'
        if (this.studentSearch) {
          url = url + '?search=' + this.studentSearch
        }
        var response = await fetch(url, {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.students = data
        }
      } catch (error) {
        console.log('Error loading students')
      }
    },

    async loadJobs() {
      try {
        var response = await fetch('http://localhost:5000/api/admin/jobs', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.jobs = data
        }
      } catch (error) {
        console.log('Error loading jobs')
      }
    },

    async loadApplications() {
      try {
        var response = await fetch('http://localhost:5000/api/admin/applications', {
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.applications = data
        }
      } catch (error) {
        console.log('Error loading applications')
      }
    },

    searchCompanies() {
      this.loadCompanies()
    },

    searchStudents() {
      this.loadStudents()
    },

    async approveCompany(companyId) {
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/companies/' + companyId + '/approve', {
          method: 'PUT',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadCompanies()
          this.loadStats()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Error approving company')
      }
    },

    async removeCompany(companyId) {
      if (!confirm('Are you sure you want to remove this company?')) return
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/companies/' + companyId + '/remove', {
          method: 'DELETE',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadCompanies()
          this.loadStats()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Error removing company')
      }
    },

    async blacklistCompany(companyId) {
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/companies/' + companyId + '/blacklist', {
          method: 'PUT',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadCompanies()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Error updating company')
      }
    },

    async blacklistStudent(studentId) {
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/students/' + studentId + '/blacklist', {
          method: 'PUT',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadStudents()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Error updating student')
      }
    },

    async removeStudent(studentId) {
      if (!confirm('Are you sure you want to remove this student?')) return
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/students/' + studentId + '/remove', {
          method: 'DELETE',
          headers: { 'Authentication-Token': this.getToken() }
        })
        var data = await response.json()
        if (response.ok) {
          this.showSuccess(data.message)
          this.loadStudents()
          this.loadStats()
        } else {
          this.showError(data.message)
        }
      } catch (error) {
        this.showError('Error removing student')
      }
    },

    async approveJob(jobId) {
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/jobs/' + jobId + '/approve', {
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
        this.showError('Error approving job')
      }
    },

    async removeJob(jobId) {
      if (!confirm('Are you sure you want to remove this job posting?')) return
      this.clearMessages()
      try {
        var response = await fetch('http://localhost:5000/api/admin/jobs/' + jobId + '/remove', {
          method: 'DELETE',
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
        this.showError('Error removing job')
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
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

.stat-pending {
  border-left: 4px solid #e67e22;
}

.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-bottom: 2px solid #ddd;
}

.tabs button {
  padding: 10px 25px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 15px;
  color: #7f8c8d;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.tabs button.active {
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  font-weight: bold;
}

.tabs button:hover {
  color: #2c3e50;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 20px;
}

.search-box input {
  padding: 8px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 300px;
}

.search-box input:focus {
  outline: none;
  border-color: #3498db;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table thead {
  background-color: #2c3e50;
  color: white;
}

.data-table th {
  padding: 12px 15px;
  text-align: left;
  font-size: 13px;
}

.data-table td {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  font-size: 13px;
}

.data-table tr:hover {
  background-color: #f8f9fa;
}

.badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
}

.badge.approved {
  background-color: #d4edda;
  color: #155724;
}

.badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.badge.blacklisted {
  background-color: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-approve {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-approve:hover {
  background-color: #219a52;
}

.btn-blacklist {
  background-color: #e67e22;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-blacklist:hover {
  background-color: #d35400;
}

.btn-remove {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-remove:hover {
  background-color: #c0392b;
}

.no-data {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-box {
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.message-box.success {
  background-color: #d4edda;
  color: #155724;
}

.message-box.error {
  background-color: #f8d7da;
  color: #721c24;
}
</style>
