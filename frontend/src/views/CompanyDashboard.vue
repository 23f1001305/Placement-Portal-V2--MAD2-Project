<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Company Dashboard</h1>
      <p>Welcome, {{ companyName }}!</p>
    </div>

    <div class="stats-container">
      <div class="stat-card">
        <h3>Job Postings</h3>
        <p class="stat-number">0</p>
      </div>
      <div class="stat-card">
        <h3>Applications Received</h3>
        <p class="stat-number">0</p>
      </div>
      <div class="stat-card">
        <h3>Shortlisted</h3>
        <p class="stat-number">0</p>
      </div>
    </div>

    <div class="dashboard-content">
      <p>Company management features will be added in the next milestone.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDashboard',
  data() {
    return {
      companyName: ''
    }
  },
  mounted() {
    this.loadCompanyInfo()
  },
  methods: {
    async loadCompanyInfo() {
      try {
        var token = localStorage.getItem('token')
        var response = await fetch('http://localhost:5000/api/current_user', {
          headers: {
            'Authentication-Token': token
          }
        })
        var data = await response.json()
        if (response.ok) {
          this.companyName = data.company_name || 'Company'
        }
      } catch (error) {
        this.companyName = 'Company'
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
  margin-bottom: 30px;
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
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  min-width: 200px;
  text-align: center;
}

.stat-card h3 {
  color: #7f8c8d;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-number {
  color: #2c3e50;
  font-size: 36px;
  font-weight: bold;
}

.dashboard-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #7f8c8d;
}
</style>
