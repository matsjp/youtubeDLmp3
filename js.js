// ==UserScript==
// @name        YoutubeURI
// @namespace   MatsPedersen@protonmail.com
// @include     https://www.youtube.com/*
// @version     1
// @grant       none
// ==/UserScript==
var a = document.createElement("a");
var loc = window.location.href;
var url = loc.substring(32);
a.href = 'vidToList:' + url;
a.appendChild(document.createTextNode("Download"));
document.getElementsByTagName("body")[0].appendChild(a);
a.style.position = "fixed";
a.style.top = "15%";
a.style.left = "10%";

function linkUpdate(){
  url = window.location.href.substring(32);
  a.href = 'vidToList:' + url;
}

window.setInterval(linkUpdate, 1000)