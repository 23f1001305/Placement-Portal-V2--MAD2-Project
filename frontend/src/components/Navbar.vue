<template>
  <nav class="navbar">
    <div class="navbar-left">
      <img src="https://via.placeholder.com/40x40?text=Logo" alt="Logo" class="logo" />
      <span class="brand-name">Placement Portal</span>
    </div>
    <div class="navbar-right">
      <span class="user-email">{{ email }}</span>
      <span class="user-role">({{ role }})</span>
      <button class="logout-btn" @click="logout">Logout</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      email: localStorage.getItem('email') || '',
      role: localStorage.getItem('role') || ''
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
      localStorage.removeItem('user_id')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #2c3e50;
  color: white;
  padding: 10px 20px;
  height: 60px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 5px;
}

.brand-name {
  font-size: 20px;
  font-weight: bold;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-email {
  font-size: 14px;
}

.user-role {
  font-size: 13px;
  color: #bdc3c7;
}

.logout-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: #c0392b;
}
</style>
