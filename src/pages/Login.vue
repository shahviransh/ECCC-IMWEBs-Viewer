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
                            <input id="password" type="password" v-model="password" class="formControl" maxlength="50"
                                required autocomplete="current-password" />
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
            error: ''
        };
    },
    props: {
        isAuthenticated: Boolean
    },
    methods: {
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
        if (window.isTauri !== undefined) {
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
}

.loginDiv {
    position: absolute;
    flex-direction: row;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    width: 430px;
    height: 100%;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.3);
}

.BackgroundVideo {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    opacity: 0.8;
}

.loginPanel {
    position: absolute;
    min-height: 100vh;
    width: 100%;
    background-color: white;
    opacity: 0.3;
}

.panel-body fieldset {
    margin: 20px;
}

.site-logo {
    margin: 25% 0;
    text-align: center;
}

.panel-title {
    text-align: center;
    font-weight: bold;
}

.formGroup {
    margin-bottom: 15px;
}

.formControl {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.loginButton {
    width: 100%;
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.loginButton:hover {
    background-color: #0056b3;
}

.errorMessage {
    color: red;
    margin-top: 10px;
}
</style>