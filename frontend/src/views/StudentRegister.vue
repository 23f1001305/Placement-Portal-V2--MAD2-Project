<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-header">
        <img src="https://via.placeholder.com/80x80?text=Logo" alt="Logo" class="register-logo" />
        <h2>Student Registration</h2>
        <p>Create your student account</p>
      </div>

      <div class="error-msg" v-if="errorMessage">
        {{ errorMessage }}
      </div>

      <div class="success-msg" v-if="successMessage">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Full Name</label>
          <input type="text" v-model="full_name" placeholder="Enter your full name" required />
        </div>

        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" placeholder="Enter your email" required />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" placeholder="Enter your password" required />
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input type="password" v-model="confirm_password" placeholder="Confirm your password" required />
        </div>

        <button type="submit" class="register-btn">Register</button>
      </form>

      <div class="login-link">
        <p>Already have an account? <router-link to="/login" class="link">Login here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentRegister',
  data() {
    return {
      full_name: '',
      email: '',
      password: '',
      confirm_password: '',
      errorMessage: '',
      successMessage: ''
    }
  },
  methods: {
    async handleRegister() {
      this.errorMessage = ''
      this.successMessage = ''

      if (this.password !== this.confirm_password) {
        this.errorMessage = 'Passwords do not match'
        return
      }

      if (this.password.length < 6) {
        this.errorMessage = 'Password must be at least 6 characters'
        return
      }

      try {
        var response = await fetch('http://localhost:5000/api/register/student', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            full_name: this.full_name,
            email: this.email,
            password: this.password
          })
        })

        var data = await response.json()

        if (response.ok) {
          this.successMessage = data.message
          this.full_name = ''
          this.email = ''
          this.password = ''
          this.confirm_password = ''
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
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
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #ecf0f1;
}

.register-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
}

.register-header {
  text-align: center;
  margin-bottom: 25px;
}

.register-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 10px;
}

.register-header h2 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.register-header p {
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
  border-color: #27ae60;
}

.register-btn {
  width: 100%;
  padding: 12px;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.register-btn:hover {
  background-color: #219a52;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
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
