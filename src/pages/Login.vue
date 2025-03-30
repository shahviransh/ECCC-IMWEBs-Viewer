<template>
    <video class="BackgroundVideo" autoplay muted loop>
        <source src="../assets/BackGround.mp4" type="video/mp4" />
        Your browser does not support HTML5 video.
    </video>
    <div class="loginDiv">
        <div class="loginPanel">
            <div class="site-logo">
            </div>
            <div class="panel-body">
                <fieldset>
                    <legend class="panel-title">Sign in to IMWEBs Viewer</legend>
                    <form @submit.prevent="login(false)">
                        <div class="formGroup">
                            <label for="username"><b>Email address:</b></label>
                            <input id="username" type="text" v-model="username" class="formControl" maxlength="50"
                                required autocomplete="username" />
                        </div>
                        <div class="formGroup">
                            <label for="password"><b>Password:</b></label>
                            <div class="passwordWrapper">
                                <input id="password" :type="showPassword ? 'text' : 'password'" v-model="password"
                                    class="formControl" maxlength="50" required autocomplete="current-password" />
                                <span class="togglePassword" @click="togglePasswordVisibility">
                                    <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" class="eyeIcon"
                                        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                        stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="eyeIcon" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round">
                                        <path d="M2 12s4-5 10-5 10 5 10 5-4 5-10 5-10-5-10-5z"></path>
                                        <path d="M4 18l1-2"></path>
                                        <path d="M8 20l1-2"></path>
                                        <path d="M16 20l-1-2"></path>
                                        <path d="M20 18l-1-2"></path>
                                    </svg>
                                </span>
                            </div>
                        </div>
                        <button type="submit" class="loginButton">Sign in</button>
                        <p v-if="error" class="errorMessage">{{ error }}</p>
                    </form>
                </fieldset>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            username: '',
            password: '',
            error: '',
            showPassword: false
        };
    },
    props: {
        isAuthenticated: Boolean
    },
    methods: {
        togglePasswordVisibility() {
            this.showPassword = !this.showPassword;
        },
        async login(autoLogin) {
            try {
                const credentials = autoLogin
                    ? { username: 'admin', password: 'admin' }
                    : { username: this.username, password: this.password };

                const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/login`, credentials);
                const token = response.data.access_token;
                localStorage.setItem('token', token);
                this.$emit("update:isAuthenticated", true);
            } catch (err) {
                console.error(err);
                this.error = err.response?.data?.error || 'Invalid username or password';
            }
        }
    },
    mounted() {
        // Auto login in Tauri
        if (window.__TAURI__) {
            this.login(true);
        }
    }
};
</script>

<style scoped>
/* Author: Dr. Michael Yu
   GitHub: https://github.com/hawklorry/Ecosystem-Services-Assessment-Tool/blob/master/src/AgBMTool.Front/ClientApp/src/app/login/login.component.css */
html,
body {
    position: relative;
    min-height: 100vh;
    margin: 0;
    font-family: Avenir, Helvetica, Arial, sans-serif;
}

.loginDiv {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    padding: 20px;
}

.BackgroundVideo {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    opacity: 0.8;
    z-index: -1;
}

.loginPanel {
    text-align: center;
}

.site-logo {
    margin: 20px 0;
}

.panel-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 20px;
    color: #333;
}

.formGroup {
    margin-bottom: 15px;
    text-align: left;
}

.formGroup label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
}

.formControl {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}

.formControl:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.loginButton {
    width: 100%;
    padding: 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    margin-top: 10px;
    transition: background-color 0.3s ease;
}

.loginButton:hover {
    background-color: #0056b3;
}

.errorMessage {
    color: red;
    margin-top: 10px;
    font-size: 0.9rem;
    text-align: left;
}

.passwordWrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.passwordWrapper .formControl {
    flex: 1;
}

.togglePassword {
    position: absolute;
    cursor: pointer;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #007bff;
}

.togglePassword:hover {
    color: #0056b3;
}

.eyeIcon {
    width: 20px;
    height: 20px;
}
</style>