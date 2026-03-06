<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <img src="https://via.placeholder.com/80x80?text=Logo" alt="Logo" class="login-logo" />
        <h2>Placement Portal</h2>
        <p>Login to your account</p>
      </div>

      <div class="error-msg" v-if="errorMessage">
        {{ errorMessage }}
      </div>

      <div class="success-msg" v-if="successMessage">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" placeholder="Enter your email" required />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" placeholder="Enter your password" required />
        </div>

        <button type="submit" class="login-btn">Login</button>
      </form>

      <div class="register-links">
        <p>Don't have an account?</p>
        <router-link to="/register/student" class="link">Register as Student</router-link>
        <span> | </span>
        <router-link to="/register/company" class="link">Register as Company</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      successMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.successMessage = ''

      try {
        var response = await fetch('http://localhost:5000/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        })

        var data = await response.json()

        if (response.ok) {
          localStorage.setItem('token', data.token)
          localStorage.setItem('role', data.role)
          localStorage.setItem('email', data.email)
          localStorage.setItem('user_id', data.user_id)

          if (data.role === 'Admin') {
            this.$router.push('/admin/dashboard')
          } else if (data.role === 'Company') {
            this.$router.push('/company/dashboard')
          } else if (data.role === 'Student') {
            this.$router.push('/student/dashboard')
          }
        } else {
          this.errorMessage = data.message
        }
      } catch (error) {
        this.errorMessage = 'Server error. Please try again later.'
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #ecf0f1;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 25px;
}

.login-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 10px;
}

.login-header h2 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.login-header p {
  color: #7f8c8d;
  font-size: 14px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 14px;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.login-btn:hover {
  background-color: #2980b9;
}

.register-links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}

.register-links p {
  margin-bottom: 5px;
  color: #7f8c8d;
}

.link {
  color: #3498db;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.error-msg {
  background-color: #fee;
  color: #e74c3c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
}

.success-msg {
  background-color: #efd;
  color: #27ae60;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
}
</style>
