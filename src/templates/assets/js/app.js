window.$ = window.jQuery = require('jquery');
import 'startbootstrap-sb-admin-2/js/sb-admin-2'
import Vue from 'vue';
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

const options = {
    // set default options here
};

window.Vue = Vue
window.axios = require("axios");

Vue.component('create-product', require('./components/product/CreateProduct.vue').default)
Vue.component('edit-product', require('./components/product/EditProduct.vue').default)

Vue.use(Toast, options);

const app = new Vue({
    el: '#app'
})