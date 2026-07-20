<!doctype html>
<html lang="en-US" class="no-js">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" /><script type="text/javascript" nonce="a612bd30df">
window.dataLayer = window.dataLayer ||[];
function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{
  'ad_storage':'denied',
  'analytics_storage':'denied',
  'ad_user_data':'denied',
  'ad_personalization':'denied',
  'personalization_storage':'denied',
  'functionality_storage':'granted',
  'security_storage':'granted',
  'wait_for_update': 500
});
gtag('set', 'ads_data_redaction', true);
gtag('set', 'url_passthrough',true);
</script>
<script src="https://cmp.osano.com/16A0DbT9yDNIaQkvZ/31b1b91a-e0b6-47ea-bde2-7f2bd13dbe5c/osano.js"></script>
<title>PyTorch 2.2: FlashAttention-v2 integration, AOTInductor &#8211; PyTorch</title>
<meta name='robots' content='max-image-preview:large' />
<link rel='dns-prefetch' href='//use.fontawesome.com' />
<link rel="alternate" type="application/rss+xml" title="PyTorch &raquo; Feed" href="https://pytorch.org/feed/" />
<link rel="alternate" type="application/rss+xml" title="PyTorch &raquo; Comments Feed" href="https://pytorch.org/comments/feed/" />
<link rel="alternate" type="text/calendar" title="PyTorch &raquo; iCal Feed" href="https://pytorch.org/event-calendar/?ical=1" />
<script src="https://lfx-segment.platform.linuxfoundation.org/latest/lfx-segment-analytics.min.js"></script>
<script type="text/javascript" nonce="a612bd30df">
 if(window.LfxAnalytics&&window.LfxAnalytics.LfxSegmentsAnalytics){var analytics=window.LfxAnalytics.LfxSegmentsAnalytics.getInstance();analytics.init().then(function(){}).catch(function(error){console.error('Failed to initialize analytics:',error)});}else{console.warn('LfxAnalytics not found');}</script>
<style id="wp-img-auto-sizes-contain-inline-css">
img:is([sizes=auto i],[sizes^="auto," i]){contain-intrinsic-size:3000px 1500px}
/*# sourceURL=wp-img-auto-sizes-contain-inline-css */
</style>
<link rel='stylesheet' id='tribe-events-pro-mini-calendar-block-styles-css' href='https://pytorch.org/wp-content/plugins/events-calendar-pro/build/css/tribe-events-pro-mini-calendar-block.css?ver=7.7.14' media='all' />
<style id="wp-emoji-styles-inline-css">

	img.wp-smiley, img.emoji {
		display: inline !important;
		border: none !important;
		box-shadow: none !important;
		height: 1em !important;
		width: 1em !important;
		margin: 0 0.07em !important;
		vertical-align: -0.1em !important;
		background: none !important;
		padding: 0 !important;
	}
/*# sourceURL=wp-emoji-styles-inline-css */
</style>
<style id="wp-block-library-inline-css">
:root{--wp-block-synced-color:#7a00df;--wp-block-synced-color--rgb:122,0,223;--wp-bound-block-color:var(--wp-block-synced-color);--wp-editor-canvas-background:#ddd;--wp-admin-theme-color:#007cba;--wp-admin-theme-color--rgb:0,124,186;--wp-admin-theme-color-darker-10:#006ba1;--wp-admin-theme-color-darker-10--rgb:0,107,160.5;--wp-admin-theme-color-darker-20:#005a87;--wp-admin-theme-color-darker-20--rgb:0,90,135;--wp-admin-border-width-focus:2px}@media (min-resolution:192dpi){:root{--wp-admin-border-width-focus:1.5px}}.wp-element-button{cursor:pointer}:root .has-very-light-gray-background-color{background-color:#eee}:root .has-very-dark-gray-background-color{background-color:#313131}:root .has-very-light-gray-color{color:#eee}:root .has-very-dark-gray-color{color:#313131}:root .has-vivid-green-cyan-to-vivid-cyan-blue-gradient-background{background:linear-gradient(135deg,#00d084,#0693e3)}:root .has-purple-crush-gradient-background{background:linear-gradient(135deg,#34e2e4,#4721fb 50%,#ab1dfe)}:root .has-hazy-dawn-gradient-background{background:linear-gradient(135deg,#faaca8,#dad0ec)}:root .has-subdued-olive-gradient-background{background:linear-gradient(135deg,#fafae1,#67a671)}:root .has-atomic-cream-gradient-background{background:linear-gradient(135deg,#fdd79a,#004a59)}:root .has-nightshade-gradient-background{background:linear-gradient(135deg,#330968,#31cdcf)}:root .has-midnight-gradient-background{background:linear-gradient(135deg,#020381,#2874fc)}:root{--wp--preset--font-size--normal:16px;--wp--preset--font-size--huge:42px}.has-regular-font-size{font-size:1em}.has-larger-font-size{font-size:2.625em}.has-normal-font-size{font-size:var(--wp--preset--font-size--normal)}.has-huge-font-size{font-size:var(--wp--preset--font-size--huge)}:root .has-text-align-center{text-align:center}:root .has-text-align-left{text-align:left}:root .has-text-align-right{text-align:right}.has-fit-text{white-space:nowrap!important}#end-resizable-editor-section{display:none}.aligncenter{clear:both}.items-justified-left{justify-content:flex-start}.items-justified-center{justify-content:center}.items-justified-right{justify-content:flex-end}.items-justified-space-between{justify-content:space-between}.screen-reader-text{word-wrap:normal!important;border:0;clip-path:inset(50%);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;width:1px}.screen-reader-text:focus{background-color:#ddd;clip-path:none;color:#444;display:block;font-size:1em;height:auto;left:5px;line-height:normal;padding:15px 23px 14px;text-decoration:none;top:5px;width:auto;z-index:100000}html :where(.has-border-color){border-style:solid}html :where([style*=border-color]){border-style:solid}html :where([style*=border-top-color]){border-top-style:solid}html :where([style*=border-right-color]){border-right-style:solid}html :where([style*=border-bottom-color]){border-bottom-style:solid}html :where([style*=border-left-color]){border-left-style:solid}html :where([style*=border-width]){border-style:solid}html :where([style*=border-top-width]){border-top-style:solid}html :where([style*=border-right-width]){border-right-style:solid}html :where([style*=border-bottom-width]){border-bottom-style:solid}html :where([style*=border-left-width]){border-left-style:solid}html :where(img[class*=wp-image-]){height:auto;max-width:100%}:where(figure){margin:0 0 1em}html :where(.is-position-sticky){--wp-admin--admin-bar--position-offset:var(--wp-admin--admin-bar--height,0px)}@media screen and (max-width:600px){html :where(.is-position-sticky){--wp-admin--admin-bar--position-offset:0px}}

/*# sourceURL=/wp-includes/css/dist/block-library/common.min.css */
</style>
<style id="wp-block-heading-inline-css">
h1:where(.wp-block-heading).has-background,h2:where(.wp-block-heading).has-background,h3:where(.wp-block-heading).has-background,h4:where(.wp-block-heading).has-background,h5:where(.wp-block-heading).has-background,h6:where(.wp-block-heading).has-background{padding:1.25em 2.375em}h1.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h1.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]),h2.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h2.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]),h3.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h3.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]),h4.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h4.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]),h5.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h5.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]),h6.has-text-align-left[style*=writing-mode]:where([style*=vertical-lr]),h6.has-text-align-right[style*=writing-mode]:where([style*=vertical-rl]){rotate:180deg}
/*# sourceURL=https://pytorch.org/wp-includes/blocks/heading/style.min.css */
</style>
<style id="wp-block-list-inline-css">
ol,ul{box-sizing:border-box}:root :where(.wp-block-list.has-background){padding:1.25em 2.375em}
/*# sourceURL=https://pytorch.org/wp-includes/blocks/list/style.min.css */
</style>
<style id="wp-block-paragraph-inline-css">
.is-small-text{font-size:.875em}.is-regular-text{font-size:1em}.is-large-text{font-size:2.25em}.is-larger-text{font-size:3em}.has-drop-cap:not(:focus):first-letter{float:left;font-size:8.4em;font-style:normal;font-weight:100;line-height:.68;margin:.05em .1em 0 0;text-transform:uppercase}body.rtl .has-drop-cap:not(:focus):first-letter{float:none;margin-left:.1em}p.has-drop-cap.has-background{overflow:hidden}:root :where(p.has-background){padding:1.25em 2.375em}:where(p.has-text-color:not(.has-link-color)) a{color:inherit}p.has-text-align-left[style*="writing-mode:vertical-lr"],p.has-text-align-right[style*="writing-mode:vertical-rl"]{rotate:180deg}
/*# sourceURL=https://pytorch.org/wp-includes/blocks/paragraph/style.min.css */
</style>
<style id="wp-block-table-inline-css">
.wp-block-table{overflow-x:auto}.wp-block-table table{border-collapse:collapse;width:100%}.wp-block-table thead{border-bottom:3px solid}.wp-block-table tfoot{border-top:3px solid}.wp-block-table td,.wp-block-table th{border:1px solid;padding:.5em}.wp-block-table .has-fixed-layout{table-layout:fixed;width:100%}.wp-block-table .has-fixed-layout td,.wp-block-table .has-fixed-layout th{word-break:break-word}.wp-block-table.aligncenter,.wp-block-table.alignleft,.wp-block-table.alignright{display:table;width:auto}.wp-block-table.aligncenter td,.wp-block-table.aligncenter th,.wp-block-table.alignleft td,.wp-block-table.alignleft th,.wp-block-table.alignright td,.wp-block-table.alignright th{word-break:break-word}.wp-block-table .has-subtle-light-gray-background-color{background-color:#f3f4f5}.wp-block-table .has-subtle-pale-green-background-color{background-color:#e9fbe5}.wp-block-table .has-subtle-pale-blue-background-color{background-color:#e7f5fe}.wp-block-table .has-subtle-pale-pink-background-color{background-color:#fcf0ef}.wp-block-table.is-style-stripes{background-color:initial;border-collapse:inherit;border-spacing:0}.wp-block-table.is-style-stripes tbody tr:nth-child(odd){background-color:#f0f0f0}.wp-block-table.is-style-stripes.has-subtle-light-gray-background-color tbody tr:nth-child(odd){background-color:#f3f4f5}.wp-block-table.is-style-stripes.has-subtle-pale-green-background-color tbody tr:nth-child(odd){background-color:#e9fbe5}.wp-block-table.is-style-stripes.has-subtle-pale-blue-background-color tbody tr:nth-child(odd){background-color:#e7f5fe}.wp-block-table.is-style-stripes.has-subtle-pale-pink-background-color tbody tr:nth-child(odd){background-color:#fcf0ef}.wp-block-table.is-style-stripes td,.wp-block-table.is-style-stripes th{border-color:#0000}.wp-block-table.is-style-stripes{border-bottom:1px solid #f0f0f0}.wp-block-table .has-border-color td,.wp-block-table .has-border-color th,.wp-block-table .has-border-color tr,.wp-block-table .has-border-color>*{border-color:inherit}.wp-block-table table[style*=border-top-color] tr:first-child,.wp-block-table table[style*=border-top-color] tr:first-child td,.wp-block-table table[style*=border-top-color] tr:first-child th,.wp-block-table table[style*=border-top-color]>*,.wp-block-table table[style*=border-top-color]>* td,.wp-block-table table[style*=border-top-color]>* th{border-top-color:inherit}.wp-block-table table[style*=border-top-color] tr:not(:first-child){border-top-color:initial}.wp-block-table table[style*=border-right-color] td:last-child,.wp-block-table table[style*=border-right-color] th,.wp-block-table table[style*=border-right-color] tr,.wp-block-table table[style*=border-right-color]>*{border-right-color:inherit}.wp-block-table table[style*=border-bottom-color] tr:last-child,.wp-block-table table[style*=border-bottom-color] tr:last-child td,.wp-block-table table[style*=border-bottom-color] tr:last-child th,.wp-block-table table[style*=border-bottom-color]>*,.wp-block-table table[style*=border-bottom-color]>* td,.wp-block-table table[style*=border-bottom-color]>* th{border-bottom-color:inherit}.wp-block-table table[style*=border-bottom-color] tr:not(:last-child){border-bottom-color:initial}.wp-block-table table[style*=border-left-color] td:first-child,.wp-block-table table[style*=border-left-color] th,.wp-block-table table[style*=border-left-color] tr,.wp-block-table table[style*=border-left-color]>*{border-left-color:inherit}.wp-block-table table[style*=border-style] td,.wp-block-table table[style*=border-style] th,.wp-block-table table[style*=border-style] tr,.wp-block-table table[style*=border-style]>*{border-style:inherit}.wp-block-table table[style*=border-width] td,.wp-block-table table[style*=border-width] th,.wp-block-table table[style*=border-width] tr,.wp-block-table table[style*=border-width]>*{border-style:inherit;border-width:inherit}
/*# sourceURL=https://pytorch.org/wp-includes/blocks/table/style.min.css */
</style>


<style id="global-styles-inline-css">
:root{--wp--preset--aspect-ratio--square: 1;--wp--preset--aspect-ratio--4-3: 4/3;--wp--preset--aspect-ratio--3-4: 3/4;--wp--preset--aspect-ratio--3-2: 3/2;--wp--preset--aspect-ratio--2-3: 2/3;--wp--preset--aspect-ratio--16-9: 16/9;--wp--preset--aspect-ratio--9-16: 9/16;--wp--preset--color--black: #000000;--wp--preset--color--cyan-bluish-gray: #abb8c3;--wp--preset--color--white: #ffffff;--wp--preset--color--pale-pink: #f78da7;--wp--preset--color--vivid-red: #cf2e2e;--wp--preset--color--luminous-vivid-orange: #ff6900;--wp--preset--color--luminous-vivid-amber: #fcb900;--wp--preset--color--light-green-cyan: #7bdcb5;--wp--preset--color--vivid-green-cyan: #00d084;--wp--preset--color--pale-cyan-blue: #8ed1fc;--wp--preset--color--vivid-cyan-blue: #0693e3;--wp--preset--color--vivid-purple: #9b51e0;--wp--preset--gradient--vivid-cyan-blue-to-vivid-purple: linear-gradient(135deg,rgb(6,147,227) 0%,rgb(155,81,224) 100%);--wp--preset--gradient--light-green-cyan-to-vivid-green-cyan: linear-gradient(135deg,rgb(122,220,180) 0%,rgb(0,208,130) 100%);--wp--preset--gradient--luminous-vivid-amber-to-luminous-vivid-orange: linear-gradient(135deg,rgb(252,185,0) 0%,rgb(255,105,0) 100%);--wp--preset--gradient--luminous-vivid-orange-to-vivid-red: linear-gradient(135deg,rgb(255,105,0) 0%,rgb(207,46,46) 100%);--wp--preset--gradient--very-light-gray-to-cyan-bluish-gray: linear-gradient(135deg,rgb(238,238,238) 0%,rgb(169,184,195) 100%);--wp--preset--gradient--cool-to-warm-spectrum: linear-gradient(135deg,rgb(74,234,220) 0%,rgb(151,120,209) 20%,rgb(207,42,186) 40%,rgb(238,44,130) 60%,rgb(251,105,98) 80%,rgb(254,248,76) 100%);--wp--preset--gradient--blush-light-purple: linear-gradient(135deg,rgb(255,206,236) 0%,rgb(152,150,240) 100%);--wp--preset--gradient--blush-bordeaux: linear-gradient(135deg,rgb(254,205,165) 0%,rgb(254,45,45) 50%,rgb(107,0,62) 100%);--wp--preset--gradient--luminous-dusk: linear-gradient(135deg,rgb(255,203,112) 0%,rgb(199,81,192) 50%,rgb(65,88,208) 100%);--wp--preset--gradient--pale-ocean: linear-gradient(135deg,rgb(255,245,203) 0%,rgb(182,227,212) 50%,rgb(51,167,181) 100%);--wp--preset--gradient--electric-grass: linear-gradient(135deg,rgb(202,248,128) 0%,rgb(113,206,126) 100%);--wp--preset--gradient--midnight: linear-gradient(135deg,rgb(2,3,129) 0%,rgb(40,116,252) 100%);--wp--preset--font-size--small: 13px;--wp--preset--font-size--medium: 20px;--wp--preset--font-size--large: 36px;--wp--preset--font-size--x-large: 42px;--wp--preset--spacing--20: 0.44rem;--wp--preset--spacing--30: 0.67rem;--wp--preset--spacing--40: 1rem;--wp--preset--spacing--50: 1.5rem;--wp--preset--spacing--60: 2.25rem;--wp--preset--spacing--70: 3.38rem;--wp--preset--spacing--80: 5.06rem;--wp--preset--shadow--natural: 6px 6px 9px rgba(0, 0, 0, 0.2);--wp--preset--shadow--deep: 12px 12px 50px rgba(0, 0, 0, 0.4);--wp--preset--shadow--sharp: 6px 6px 0px rgba(0, 0, 0, 0.2);--wp--preset--shadow--outlined: 6px 6px 0px -3px rgb(255, 255, 255), 6px 6px rgb(0, 0, 0);--wp--preset--shadow--crisp: 6px 6px 0px rgb(0, 0, 0);}:root { --wp--style--global--content-size: 1300px;--wp--style--global--wide-size: 1300px; }:where(body) { margin: 0; }.wp-site-blocks > .alignleft { float: left; margin-right: 2em; }.wp-site-blocks > .alignright { float: right; margin-left: 2em; }.wp-site-blocks > .aligncenter { justify-content: center; margin-left: auto; margin-right: auto; }:where(.is-layout-flex){gap: 0.5em;}:where(.is-layout-grid){gap: 0.5em;}.is-layout-flow > .alignleft{float: left;margin-inline-start: 0;margin-inline-end: 2em;}.is-layout-flow > .alignright{float: right;margin-inline-start: 2em;margin-inline-end: 0;}.is-layout-flow > .aligncenter{margin-left: auto !important;margin-right: auto !important;}.is-layout-constrained > .alignleft{float: left;margin-inline-start: 0;margin-inline-end: 2em;}.is-layout-constrained > .alignright{float: right;margin-inline-start: 2em;margin-inline-end: 0;}.is-layout-constrained > .aligncenter{margin-left: auto !important;margin-right: auto !important;}.is-layout-constrained > :where(:not(.alignleft):not(.alignright):not(.alignfull)){max-width: var(--wp--style--global--content-size);margin-left: auto !important;margin-right: auto !important;}.is-layout-constrained > .alignwide{max-width: var(--wp--style--global--wide-size);}body .is-layout-flex{display: flex;}.is-layout-flex{flex-wrap: wrap;align-items: center;}.is-layout-flex > :is(*, div){margin: 0;}body .is-layout-grid{display: grid;}.is-layout-grid > :is(*, div){margin: 0;}body{padding-top: 0px;padding-right: 0px;padding-bottom: 0px;padding-left: 0px;}:root :where(.wp-element-button, .wp-block-button__link){background-color: #32373c;border-width: 0;color: #fff;font-family: inherit;font-size: inherit;font-style: inherit;font-weight: inherit;letter-spacing: inherit;line-height: inherit;padding-top: calc(0.667em + 2px);padding-right: calc(1.333em + 2px);padding-bottom: calc(0.667em + 2px);padding-left: calc(1.333em + 2px);text-decoration: none;text-transform: inherit;}.has-black-color{color: var(--wp--preset--color--black) !important;}.has-cyan-bluish-gray-color{color: var(--wp--preset--color--cyan-bluish-gray) !important;}.has-white-color{color: var(--wp--preset--color--white) !important;}.has-pale-pink-color{color: var(--wp--preset--color--pale-pink) !important;}.has-vivid-red-color{color: var(--wp--preset--color--vivid-red) !important;}.has-luminous-vivid-orange-color{color: var(--wp--preset--color--luminous-vivid-orange) !important;}.has-luminous-vivid-amber-color{color: var(--wp--preset--color--luminous-vivid-amber) !important;}.has-light-green-cyan-color{color: var(--wp--preset--color--light-green-cyan) !important;}.has-vivid-green-cyan-color{color: var(--wp--preset--color--vivid-green-cyan) !important;}.has-pale-cyan-blue-color{color: var(--wp--preset--color--pale-cyan-blue) !important;}.has-vivid-cyan-blue-color{color: var(--wp--preset--color--vivid-cyan-blue) !important;}.has-vivid-purple-color{color: var(--wp--preset--color--vivid-purple) !important;}.has-black-background-color{background-color: var(--wp--preset--color--black) !important;}.has-cyan-bluish-gray-background-color{background-color: var(--wp--preset--color--cyan-bluish-gray) !important;}.has-white-background-color{background-color: var(--wp--preset--color--white) !important;}.has-pale-pink-background-color{background-color: var(--wp--preset--color--pale-pink) !important;}.has-vivid-red-background-color{background-color: var(--wp--preset--color--vivid-red) !important;}.has-luminous-vivid-orange-background-color{background-color: var(--wp--preset--color--luminous-vivid-orange) !important;}.has-luminous-vivid-amber-background-color{background-color: var(--wp--preset--color--luminous-vivid-amber) !important;}.has-light-green-cyan-background-color{background-color: var(--wp--preset--color--light-green-cyan) !important;}.has-vivid-green-cyan-background-color{background-color: var(--wp--preset--color--vivid-green-cyan) !important;}.has-pale-cyan-blue-background-color{background-color: var(--wp--preset--color--pale-cyan-blue) !important;}.has-vivid-cyan-blue-background-color{background-color: var(--wp--preset--color--vivid-cyan-blue) !important;}.has-vivid-purple-background-color{background-color: var(--wp--preset--color--vivid-purple) !important;}.has-black-border-color{border-color: var(--wp--preset--color--black) !important;}.has-cyan-bluish-gray-border-color{border-color: var(--wp--preset--color--cyan-bluish-gray) !important;}.has-white-border-color{border-color: var(--wp--preset--color--white) !important;}.has-pale-pink-border-color{border-color: var(--wp--preset--color--pale-pink) !important;}.has-vivid-red-border-color{border-color: var(--wp--preset--color--vivid-red) !important;}.has-luminous-vivid-orange-border-color{border-color: var(--wp--preset--color--luminous-vivid-orange) !important;}.has-luminous-vivid-amber-border-color{border-color: var(--wp--preset--color--luminous-vivid-amber) !important;}.has-light-green-cyan-border-color{border-color: var(--wp--preset--color--light-green-cyan) !important;}.has-vivid-green-cyan-border-color{border-color: var(--wp--preset--color--vivid-green-cyan) !important;}.has-pale-cyan-blue-border-color{border-color: var(--wp--preset--color--pale-cyan-blue) !important;}.has-vivid-cyan-blue-border-color{border-color: var(--wp--preset--color--vivid-cyan-blue) !important;}.has-vivid-purple-border-color{border-color: var(--wp--preset--color--vivid-purple) !important;}.has-vivid-cyan-blue-to-vivid-purple-gradient-background{background: var(--wp--preset--gradient--vivid-cyan-blue-to-vivid-purple) !important;}.has-light-green-cyan-to-vivid-green-cyan-gradient-background{background: var(--wp--preset--gradient--light-green-cyan-to-vivid-green-cyan) !important;}.has-luminous-vivid-amber-to-luminous-vivid-orange-gradient-background{background: var(--wp--preset--gradient--luminous-vivid-amber-to-luminous-vivid-orange) !important;}.has-luminous-vivid-orange-to-vivid-red-gradient-background{background: var(--wp--preset--gradient--luminous-vivid-orange-to-vivid-red) !important;}.has-very-light-gray-to-cyan-bluish-gray-gradient-background{background: var(--wp--preset--gradient--very-light-gray-to-cyan-bluish-gray) !important;}.has-cool-to-warm-spectrum-gradient-background{background: var(--wp--preset--gradient--cool-to-warm-spectrum) !important;}.has-blush-light-purple-gradient-background{background: var(--wp--preset--gradient--blush-light-purple) !important;}.has-blush-bordeaux-gradient-background{background: var(--wp--preset--gradient--blush-bordeaux) !important;}.has-luminous-dusk-gradient-background{background: var(--wp--preset--gradient--luminous-dusk) !important;}.has-pale-ocean-gradient-background{background: var(--wp--preset--gradient--pale-ocean) !important;}.has-electric-grass-gradient-background{background: var(--wp--preset--gradient--electric-grass) !important;}.has-midnight-gradient-background{background: var(--wp--preset--gradient--midnight) !important;}.has-small-font-size{font-size: var(--wp--preset--font-size--small) !important;}.has-medium-font-size{font-size: var(--wp--preset--font-size--medium) !important;}.has-large-font-size{font-size: var(--wp--preset--font-size--large) !important;}.has-x-large-font-size{font-size: var(--wp--preset--font-size--x-large) !important;}
/*# sourceURL=global-styles-inline-css */
</style>

<link rel='stylesheet' id='salient-child-featherlight-style-css' href='https://pytorch.org/wp-content/themes/salient-child/vc-addons/css/featherlight.css?ver=7.0' media='all' />
<link rel='stylesheet' id='search-filter-plugin-styles-css' href='https://pytorch.org/wp-content/plugins/search-filter-pro/public/assets/css/search-filter.min.css?ver=2.5.21' media='all' />
<link rel='stylesheet' id='salient-child-style-css' href='https://pytorch.org/wp-content/themes/salient-child/style.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='vc-addons-style-css' href='https://pytorch.org/wp-content/themes/salient-child/vc-addons/css/vc-addons.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='templates-style-css' href='https://pytorch.org/wp-content/themes/salient-child/templates/css/templates.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='widgets-style-css' href='https://pytorch.org/wp-content/themes/salient-child/widgets/css/widgets.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='results-style-css' href='https://pytorch.org/wp-content/themes/salient-child/search-filter/css/results.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='fonts-style-css' href='https://pytorch.org/wp-content/themes/salient-child/fonts/fonts.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='events-calendar-style-css' href='https://pytorch.org/wp-content/themes/salient-child/css/events-calendar.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='latest-posts-linux-style-css' href='https://pytorch.org/wp-content/themes/salient-child/vc-addons/css/latest-posts-linux.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='font-awesome-css' href='https://use.fontawesome.com/releases/v6.0.0/css/all.css?ver=6.0.0' media='all' />
<link rel='stylesheet' id='font-awesome-shim-css' href='https://use.fontawesome.com/releases/v6.0.0/css/v4-shims.css?ver=6.0.0' media='all' />
<link rel='stylesheet' id='salient-grid-system-css' href='https://pytorch.org/wp-content/themes/salient/css/build/grid-system.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='main-styles-css' href='https://pytorch.org/wp-content/themes/salient/css/build/style.css?ver=18.1.1' media='all' />
<style id="main-styles-inline-css">

		@font-face{
		     font-family:'Open Sans';
		     src:url('https://pytorch.org/wp-content/themes/salient/css/fonts/OpenSans-Light.woff') format('woff');
		     font-weight:300;
		     font-style:normal; 
		}
		 @font-face{
		     font-family:'Open Sans';
		     src:url('https://pytorch.org/wp-content/themes/salient/css/fonts/OpenSans-Regular.woff') format('woff');
		     font-weight:400;
		     font-style:normal; 
		}
		 @font-face{
		     font-family:'Open Sans';
		     src:url('https://pytorch.org/wp-content/themes/salient/css/fonts/OpenSans-SemiBold.woff') format('woff');
		     font-weight:600;
		     font-style:normal; 
		}
		 @font-face{
		     font-family:'Open Sans';
		     src:url('https://pytorch.org/wp-content/themes/salient/css/fonts/OpenSans-Bold.woff') format('woff');
		     font-weight:700;
		     font-style:normal; 
		}
/*# sourceURL=main-styles-inline-css */
</style>
<link rel='stylesheet' id='nectar-header-secondary-nav-css' href='https://pytorch.org/wp-content/themes/salient/css/build/header/header-secondary-nav.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='nectar-single-styles-css' href='https://pytorch.org/wp-content/themes/salient/css/build/single.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='nectar-element-page-submenu-css' href='https://pytorch.org/wp-content/themes/salient/css/build/elements/element-page-submenu.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='nectar-basic-events-calendar-css' href='https://pytorch.org/wp-content/themes/salient/css/build/third-party/events-calendar.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='nectar-brands-css' href='https://pytorch.org/wp-content/themes/salient/css/nectar-brands.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='responsive-css' href='https://pytorch.org/wp-content/themes/salient/css/build/responsive.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='skin-original-css' href='https://pytorch.org/wp-content/themes/salient/css/build/skin-original.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='salient-wp-menu-dynamic-css' href='https://pytorch.org/wp-content/uploads/salient/menu-dynamic.css?ver=46900' media='all' />
<link rel='stylesheet' id='dynamic-css-css' href='https://pytorch.org/wp-content/uploads/salient/salient-dynamic-styles.css?ver=69676' media='all' />
<style id="dynamic-css-inline-css">
#page-header-bg[data-post-hs="default_minimal"] .inner-wrap{text-align:center}#page-header-bg[data-post-hs="default_minimal"] .inner-wrap >a,.material #page-header-bg.fullscreen-header .inner-wrap >a{color:#fff;font-weight:600;border:var(--nectar-border-thickness) solid rgba(255,255,255,0.4);padding:4px 10px;margin:5px 6px 0px 5px;display:inline-block;transition:all 0.2s ease;-webkit-transition:all 0.2s ease;font-size:14px;line-height:18px}body.material #page-header-bg.fullscreen-header .inner-wrap >a{margin-bottom:15px;}body.material #page-header-bg.fullscreen-header .inner-wrap >a{border:none;padding:6px 10px}body[data-button-style^="rounded"] #page-header-bg[data-post-hs="default_minimal"] .inner-wrap >a,body[data-button-style^="rounded"].material #page-header-bg.fullscreen-header .inner-wrap >a{border-radius:100px}body.single [data-post-hs="default_minimal"] #single-below-header span,body.single .heading-title[data-header-style="default_minimal"] #single-below-header span{line-height:14px;}#page-header-bg[data-post-hs="default_minimal"] #single-below-header{text-align:center;position:relative;z-index:100}#page-header-bg[data-post-hs="default_minimal"] #single-below-header span{float:none;display:inline-block}#page-header-bg[data-post-hs="default_minimal"] .inner-wrap >a:hover,#page-header-bg[data-post-hs="default_minimal"] .inner-wrap >a:focus{border-color:transparent}#page-header-bg.fullscreen-header .avatar,#page-header-bg[data-post-hs="default_minimal"] .avatar{border-radius:100%}#page-header-bg.fullscreen-header .meta-author span,#page-header-bg[data-post-hs="default_minimal"] .meta-author span{display:block}#page-header-bg.fullscreen-header .meta-author img{margin-bottom:0;height:50px;width:auto}#page-header-bg[data-post-hs="default_minimal"] .meta-author img{margin-bottom:0;height:40px;width:auto}#page-header-bg[data-post-hs="default_minimal"] .author-section{position:absolute;bottom:30px}#page-header-bg.fullscreen-header .meta-author,#page-header-bg[data-post-hs="default_minimal"] .meta-author{font-size:18px}#page-header-bg.fullscreen-header .author-section .meta-date,#page-header-bg[data-post-hs="default_minimal"] .author-section .meta-date{font-size:12px;color:rgba(255,255,255,0.8)}#page-header-bg.fullscreen-header .author-section .meta-date i{font-size:12px}#page-header-bg[data-post-hs="default_minimal"] .author-section .meta-date i{font-size:11px;line-height:14px}#page-header-bg[data-post-hs="default_minimal"] .author-section .avatar-post-info{position:relative;top:-5px}#page-header-bg.fullscreen-header .author-section a,#page-header-bg[data-post-hs="default_minimal"] .author-section a{display:block;margin-bottom:-2px}#page-header-bg[data-post-hs="default_minimal"] .author-section a{font-size:14px;line-height:14px}#page-header-bg.fullscreen-header .author-section a:hover,#page-header-bg[data-post-hs="default_minimal"] .author-section a:hover{color:rgba(255,255,255,0.85)!important}#page-header-bg.fullscreen-header .author-section,#page-header-bg[data-post-hs="default_minimal"] .author-section{width:100%;z-index:10;text-align:center}#page-header-bg.fullscreen-header .author-section{margin-top:25px;}#page-header-bg.fullscreen-header .author-section span,#page-header-bg[data-post-hs="default_minimal"] .author-section span{padding-left:0;line-height:20px;font-size:20px}#page-header-bg.fullscreen-header .author-section .avatar-post-info,#page-header-bg[data-post-hs="default_minimal"] .author-section .avatar-post-info{margin-left:10px}#page-header-bg.fullscreen-header .author-section .avatar-post-info,#page-header-bg.fullscreen-header .author-section .meta-author,#page-header-bg[data-post-hs="default_minimal"] .author-section .avatar-post-info,#page-header-bg[data-post-hs="default_minimal"] .author-section .meta-author{text-align:left;display:inline-block;top:9px}@media only screen and (min-width :690px) and (max-width :999px){body.single-post #page-header-bg[data-post-hs="default_minimal"]{padding-top:10%;padding-bottom:10%;}}@media only screen and (max-width :690px){#ajax-content-wrap #page-header-bg[data-post-hs="default_minimal"] #single-below-header span:not(.rich-snippet-hidden),#ajax-content-wrap .row.heading-title[data-header-style="default_minimal"] .col.section-title span.meta-category{display:inline-block;}.container-wrap[data-remove-post-comment-number="0"][data-remove-post-author="0"][data-remove-post-date="0"] .heading-title[data-header-style="default_minimal"] #single-below-header > span,#page-header-bg[data-post-hs="default_minimal"] .span_6[data-remove-post-comment-number="0"][data-remove-post-author="0"][data-remove-post-date="0"] #single-below-header > span{padding:0 8px;}.container-wrap[data-remove-post-comment-number="0"][data-remove-post-author="0"][data-remove-post-date="0"] .heading-title[data-header-style="default_minimal"] #single-below-header span,#page-header-bg[data-post-hs="default_minimal"] .span_6[data-remove-post-comment-number="0"][data-remove-post-author="0"][data-remove-post-date="0"] #single-below-header span{font-size:13px;line-height:10px;}.material #page-header-bg.fullscreen-header .author-section{margin-top:5px;}#page-header-bg.fullscreen-header .author-section{bottom:20px;}#page-header-bg.fullscreen-header .author-section .meta-date:not(.updated){margin-top:-4px;display:block;}#page-header-bg.fullscreen-header .author-section .avatar-post-info{margin:10px 0 0 0;}}#page-header-bg h1,#page-header-bg .subheader,.nectar-box-roll .overlaid-content h1,.nectar-box-roll .overlaid-content .subheader,#page-header-bg #portfolio-nav a i,body .section-title #portfolio-nav a:hover i,.page-header-no-bg h1,.page-header-no-bg span,#page-header-bg #portfolio-nav a i,#page-header-bg span,#page-header-bg #single-below-header a:hover,#page-header-bg #single-below-header a:focus,#page-header-bg.fullscreen-header .author-section a{color:#ffffff!important;}body #page-header-bg .pinterest-share i,body #page-header-bg .facebook-share i,body #page-header-bg .linkedin-share i,body #page-header-bg .twitter-share i,body #page-header-bg .google-plus-share i,body #page-header-bg .icon-salient-heart,body #page-header-bg .icon-salient-heart-2{color:#ffffff;}#page-header-bg[data-post-hs="default_minimal"] .inner-wrap > a:not(:hover){color:#ffffff;border-color:rgba(255,255,255,0.4);}.single #page-header-bg #single-below-header > span{border-color:rgba(255,255,255,0.4);}body .section-title #portfolio-nav a:hover i{opacity:0.75;}.single #page-header-bg .blog-title #single-meta .nectar-social.hover > div a,.single #page-header-bg .blog-title #single-meta > div a,.single #page-header-bg .blog-title #single-meta ul .n-shortcode a,#page-header-bg .blog-title #single-meta .nectar-social.hover .share-btn{border-color:rgba(255,255,255,0.4);}.single #page-header-bg .blog-title #single-meta .nectar-social.hover > div a:hover,#page-header-bg .blog-title #single-meta .nectar-social.hover .share-btn:hover,.single #page-header-bg .blog-title #single-meta div > a:hover,.single #page-header-bg .blog-title #single-meta ul .n-shortcode a:hover,.single #page-header-bg .blog-title #single-meta ul li:not(.meta-share-count):hover > a{border-color:rgba(255,255,255,1);}.single #page-header-bg #single-meta div span,.single #page-header-bg #single-meta > div a,.single #page-header-bg #single-meta > div i{color:#ffffff!important;}.single #page-header-bg #single-meta ul .meta-share-count .nectar-social a i{color:rgba(255,255,255,0.7)!important;}.single #page-header-bg #single-meta ul .meta-share-count .nectar-social a:hover i{color:rgba(255,255,255,1)!important;}#header-space{background-color:#ffffff}@media only screen and (min-width:1000px){body #ajax-content-wrap.no-scroll{min-height:calc(100vh - 114px);height:calc(100vh - 114px)!important;}}@media only screen and (min-width:1000px){#page-header-wrap.fullscreen-header,#page-header-wrap.fullscreen-header #page-header-bg,html:not(.nectar-box-roll-loaded) .nectar-box-roll > #page-header-bg.fullscreen-header,.nectar_fullscreen_zoom_recent_projects,#nectar_fullscreen_rows:not(.afterLoaded) > div{height:calc(100vh - 113px);}.wpb_row.vc_row-o-full-height.top-level,.wpb_row.vc_row-o-full-height.top-level > .col.span_12{min-height:calc(100vh - 113px);}html:not(.nectar-box-roll-loaded) .nectar-box-roll > #page-header-bg.fullscreen-header{top:114px;}.nectar-slider-wrap[data-fullscreen="true"]:not(.loaded),.nectar-slider-wrap[data-fullscreen="true"]:not(.loaded) .swiper-container{height:calc(100vh - 112px)!important;}.admin-bar .nectar-slider-wrap[data-fullscreen="true"]:not(.loaded),.admin-bar .nectar-slider-wrap[data-fullscreen="true"]:not(.loaded) .swiper-container{height:calc(100vh - 112px - 32px)!important;}}.admin-bar[class*="page-template-template-no-header"] .wpb_row.vc_row-o-full-height.top-level,.admin-bar[class*="page-template-template-no-header"] .wpb_row.vc_row-o-full-height.top-level > .col.span_12{min-height:calc(100vh - 32px);}body[class*="page-template-template-no-header"] .wpb_row.vc_row-o-full-height.top-level,body[class*="page-template-template-no-header"] .wpb_row.vc_row-o-full-height.top-level > .col.span_12{min-height:100vh;}@media only screen and (max-width:999px){.using-mobile-browser #nectar_fullscreen_rows:not(.afterLoaded):not([data-mobile-disable="on"]) > div{height:calc(100vh - 106px);}.using-mobile-browser .wpb_row.vc_row-o-full-height.top-level,.using-mobile-browser .wpb_row.vc_row-o-full-height.top-level > .col.span_12,[data-permanent-transparent="1"].using-mobile-browser .wpb_row.vc_row-o-full-height.top-level,[data-permanent-transparent="1"].using-mobile-browser .wpb_row.vc_row-o-full-height.top-level > .col.span_12{min-height:calc(100vh - 106px);}html:not(.nectar-box-roll-loaded) .nectar-box-roll > #page-header-bg.fullscreen-header,.nectar_fullscreen_zoom_recent_projects,.nectar-slider-wrap[data-fullscreen="true"]:not(.loaded),.nectar-slider-wrap[data-fullscreen="true"]:not(.loaded) .swiper-container,#nectar_fullscreen_rows:not(.afterLoaded):not([data-mobile-disable="on"]) > div{height:calc(100vh - 53px);}.wpb_row.vc_row-o-full-height.top-level,.wpb_row.vc_row-o-full-height.top-level > .col.span_12{min-height:calc(100vh - 53px);}body[data-transparent-header="false"] #ajax-content-wrap.no-scroll{min-height:calc(100vh - 53px);height:calc(100vh - 53px);}}@media only screen and (max-width:690px){body .vc_row.bottom_padding_phone_7pct{padding-bottom:7%!important;}}@media only screen and (max-width:690px){body .vc_row.top_padding_phone_7pct{padding-top:7%!important;}}.screen-reader-text,.nectar-skip-to-content:not(:focus){border:0;clip:rect(1px,1px,1px,1px);clip-path:inset(50%);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute!important;width:1px;word-wrap:normal!important;}.row .col img:not([srcset]){width:auto;}.row .col img.img-with-animation.nectar-lazy:not([srcset]){width:100%;}
/*# sourceURL=dynamic-css-inline-css */
</style>
<link rel='stylesheet' id='pytorch-style-css' href='https://pytorch.org/wp-content/themes/salient-child/sites/pytorch/pytorch.css?ver=18.1.1' media='all' />
<link rel='stylesheet' id='prism-styles-css' href='https://pytorch.org/wp-content/themes/salient-child/vc-addons/css/prism.css?ver=18.1.1' media='all' />
<script id="jquery-core-js" src="https://pytorch.org/wp-includes/js/jquery/jquery.min.js?ver=3.7.1"></script>
<script id="jquery-migrate-js" src="https://pytorch.org/wp-includes/js/jquery/jquery-migrate.min.js?ver=3.4.1"></script>
<script id="search-filter-plugin-build-js-extra">
var SF_LDATA = {"ajax_url":"https://pytorch.org/wp-admin/admin-ajax.php","home_url":"https://pytorch.org/","extensions":[]};
//# sourceURL=search-filter-plugin-build-js-extra
</script>
<script id="search-filter-plugin-build-js" src="https://pytorch.org/wp-content/plugins/search-filter-pro/public/assets/js/search-filter-build.min.js?ver=2.5.21"></script>
<script id="search-filter-plugin-chosen-js" src="https://pytorch.org/wp-content/plugins/search-filter-pro/public/assets/js/chosen.jquery.min.js?ver=2.5.21"></script>
<script type="text/javascript" nonce="a612bd30df"></script><link rel="EditURI" type="application/rsd+xml" title="RSD" href="https://pytorch.org/xmlrpc.php?rsd" />
<meta name="generator" content="WordPress 7.0" />
<link rel="canonical" href="https://pytorch.org/blog/pytorch2-2/" />
<link rel='shortlink' href='https://pytorch.org/?p=748' />
<meta name="tec-api-version" content="v1"><meta name="tec-api-origin" content="https://pytorch.org"><link rel="alternate" href="https://pytorch.org/wp-json/tribe/events/v1/" /><script type="text/javascript" nonce="a612bd30df"> var root = document.getElementsByTagName( "html" )[0]; root.setAttribute( "class", "js" ); </script><!-- Google Tag Manager -->
<script type="text/javascript" nonce="a612bd30df">(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-T8XT4PS');</script>
<!-- End Google Tag Manager --><meta name="generator" content="Powered by WPBakery Page Builder - drag and drop page builder for WordPress."/>
<link rel="icon" href="https://pytorch.org/wp-content/uploads/2024/10/cropped-favicon-32x32.webp" sizes="32x32" />
<link rel="icon" href="https://pytorch.org/wp-content/uploads/2024/10/cropped-favicon-192x192.webp" sizes="192x192" />
<link rel="apple-touch-icon" href="https://pytorch.org/wp-content/uploads/2024/10/cropped-favicon-180x180.webp" />
<meta name="msapplication-TileImage" content="https://pytorch.org/wp-content/uploads/2024/10/cropped-favicon-270x270.webp" />
<style id="wp-custom-css">
.disabled-button {
  pointer-events: none;
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
<noscript><style> .wpb_animate_when_almost_visible { opacity: 1; }</style></noscript><link rel='stylesheet' id='js_composer_front-css' href='https://pytorch.org/wp-content/themes/salient/css/build/plugins/js_composer.css?ver=18.1.1' media='all' />
<link data-pagespeed-no-defer data-nowprocket data-wpacu-skip data-no-optimize data-noptimize rel='stylesheet' id='main-styles-non-critical-css' href='https://pytorch.org/wp-content/themes/salient/css/build/style-non-critical.css?ver=18.1.1' media='all' />
<link data-pagespeed-no-defer data-nowprocket data-wpacu-skip data-no-optimize data-noptimize rel='stylesheet' id='fancyBox-css' href='https://pytorch.org/wp-content/themes/salient/css/build/plugins/jquery.fancybox.css?ver=3.3.1' media='all' />
<link data-pagespeed-no-defer data-nowprocket data-wpacu-skip data-no-optimize data-noptimize rel='stylesheet' id='nectar-ocm-core-css' href='https://pytorch.org/wp-content/themes/salient/css/build/off-canvas/core.css?ver=18.1.1' media='all' />
<link data-pagespeed-no-defer data-nowprocket data-wpacu-skip data-no-optimize data-noptimize rel='stylesheet' id='nectar-ocm-slide-out-right-hover-css' href='https://pytorch.org/wp-content/themes/salient/css/build/off-canvas/slide-out-right-hover.css?ver=18.1.1' media='all' />

</head><body class="wp-singular post-template-default single single-post postid-748 single-format-standard wp-theme-salient wp-child-theme-salient-child tribe-no-js original language-py wpb-js-composer js-comp-ver-8.7.2 vc_responsive tribe-theme-salient" data-footer-reveal="false" data-footer-reveal-shadow="none" data-header-format="default" data-body-border="off" data-boxed-style="" data-header-breakpoint="1000" data-dropdown-style="minimal" data-cae="easeOutCubic" data-cad="750" data-megamenu-width="contained" data-aie="none" data-ls="fancybox" data-apte="standard" data-hhun="0" data-fancy-form-rcs="default" data-form-style="default" data-form-submit="regular" data-is="minimal" data-button-style="slightly_rounded" data-user-account-button="false" data-flex-cols="true" data-col-gap="default" data-header-inherit-rc="false" data-header-search="true" data-animated-anchors="true" data-ajax-transitions="false" data-full-width-header="false" data-slide-out-widget-area="true" data-slide-out-widget-area-style="slide-out-from-right-hover" data-user-set-ocm="off" data-loading-animation="none" data-bg-header="false" data-responsive="1" data-ext-responsive="true" data-ext-padding="90" data-header-resize="1" data-header-color="custom" data-cart="false" data-remove-m-parallax="" data-remove-m-video-bgs="" data-m-animate="0" data-force-header-trans-color="light" data-smooth-scrolling="0" data-permanent-transparent="false" >
    
    <script type="text/javascript" nonce="a612bd30df">
	 (function(window, document) {

		document.documentElement.classList.remove("no-js");

		if(navigator.userAgent.match(/(Android|iPod|iPhone|iPad|BlackBerry|IEMobile|Opera Mini)/)) {
			document.body.className += " using-mobile-browser mobile ";
		}
		if(navigator.userAgent.match(/Mac/) && navigator.maxTouchPoints && navigator.maxTouchPoints > 2) {
			document.body.className += " using-ios-device ";
		}

		if( !("ontouchstart" in window) ) {

			var body = document.querySelector("body");
			var winW = window.innerWidth;
			var bodyW = body.clientWidth;

			if (winW > bodyW + 4) {

				var vwTestEl = document.createElement("div");
				vwTestEl.style.position = "absolute";
				vwTestEl.style.top = "-9999px";
				vwTestEl.style.width = "100vw";
				body.appendChild(vwTestEl);
				var vwWidth = vwTestEl.offsetWidth;
				body.removeChild(vwTestEl);

				if (vwWidth > bodyW + 4) {
					body.setAttribute("style", "--scroll-bar-w: " + (winW - bodyW - 4) + "px");
				} else {
					body.setAttribute("style", "--scroll-bar-w: 0px");
				}

			} else {
				body.setAttribute("style", "--scroll-bar-w: 0px");
			}
		}

	 })(window, document);
   </script><!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-T8XT4PS"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) --><nav aria-label="Skip links" class="nectar-skip-to-content-wrap" data-nosnippet><a href="#ajax-content-wrap" class="nectar-skip-to-content">Skip to main content</a></nav>	
	<div id="header-space" data-secondary-header-display="full" data-header-mobile-fixed='1'></div> 
	
	    <div id="header-outer" data-has-menu="true" data-has-buttons="yes" data-header-button_style="default" data-using-pr-menu="false" data-mobile-fixed="1" data-ptnm="false" data-lhe="animated_underline" data-user-set-bg="#222222" data-format="default" data-permanent-transparent="false" data-megamenu-rt="0" data-remove-fixed="0" data-header-resize="1" data-cart="false" data-transparency-option="" data-box-shadow="large" data-shrink-num="6" data-using-secondary="1" data-using-logo="1" data-logo-height="40" data-m-logo-height="30" data-padding="20" data-full-width="false" data-condense="false" >
        
	<div id="header-secondary-outer" class="default" data-mobile="display_full" data-remove-fixed="0" data-lhe="animated_underline" data-secondary-text="true" data-full-width="false" data-mobile-fixed="1" data-permanent-transparent="false" >
		<div class="container">
			<nav aria-label="Secondary Navigation">
				<div class="nectar-center-text"><a href="https://events.linuxfoundation.org/pytorch-conference-north-america/">Join us at PyTorch Conference North America · Oct 20-21 · San Jose, CA</a></div>
			</nav>
		</div>
	</div>


<div id="search-outer" class="nectar" data-nosnippet>
	<div id="search">
		<div class="container">
			 <div id="search-box">
				 <div class="inner-wrap">
					 <div class="col span_12">
						  <form role="search" action="https://pytorch.org/" method="GET">
															<input type="text" name="s"  value="Start Typing..." aria-label="Search" data-placeholder="Start Typing..." />
							
						
						<button aria-label="Search" class="search-box__button" type="submit">Search</button>						</form>
					</div><!--/span_12-->
				</div><!--/inner-wrap-->
			 </div><!--/search-box-->
			 <div id="close"><a href="#" role="button"><span class="screen-reader-text">Close Search</span>
				<span class="icon-salient-x" aria-hidden="true"></span>				 </a></div>
		 </div><!--/container-->
	</div><!--/search-->
</div><!--/search-outer-->

<header id="top" role="banner" aria-label="Main Menu">
		<div class="container">
		<div class="row">
			<div class="col span_3">
								<a id="logo" href="https://pytorch.org" data-supplied-ml-starting-dark="false" data-supplied-ml-starting="false" data-supplied-ml="false" class="disable-opacity-transition">
					<img class="stnd skip-lazy" width="" height="" alt="PyTorch Logo" src="https://pytorch.org/wp-content/uploads/2024/10/logo.svg"  />				</a>
							</div><!--/span_3-->

			<div class="col span_9 col_last">
									<div class="nectar-mobile-only mobile-header"><div class="inner"></div></div>
									<a class="mobile-search" href="#searchbox"><span class="nectar-icon icon-salient-search" aria-hidden="true"></span><span class="screen-reader-text">search</span></a>
														<div class="slide-out-widget-area-toggle mobile-icon slide-out-from-right-hover" data-custom-color="false" data-icon-animation="simple-transform">
						<div> <a href="#slide-out-widget-area" role="button" aria-label="Navigation Menu" aria-expanded="false" class="closed">
							<span class="screen-reader-text">Menu</span><span aria-hidden="true"> <i class="lines-button x2"> <i class="lines"></i> </i> </span>						</a></div>
					</div>
				
									<nav aria-label="Main Menu">
													<ul class="sf-menu">
								<li id="menu-item-89" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-89"><a href="#" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">Learn</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-2296" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2296"><a href="https://pytorch.org/get-started/locally/"><span class="menu-title-text">Get Started</span></a></li>
	<li id="menu-item-90" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-90"><a href="https://pytorch.org/tutorials/"><span class="menu-title-text">Tutorials</span></a></li>
	<li id="menu-item-91" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-91"><a href="https://pytorch.org/tutorials/beginner/basics/intro.html"><span class="menu-title-text">Learn the Basics</span></a></li>
	<li id="menu-item-92" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-92"><a href="https://docs.pytorch.org/tutorials/recipes_index.html"><span class="menu-title-text">PyTorch Recipes</span></a></li>
	<li id="menu-item-93" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-93"><a href="https://pytorch.org/tutorials/beginner/introyt.html"><span class="menu-title-text">Intro to PyTorch &#8211; YouTube Series</span></a></li>
	<li id="menu-item-2200" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2200"><a href="https://pytorch.org/webinars/"><span class="menu-title-text">Webinars</span></a></li>
	<li id="menu-item-113097" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-113097"><a href="https://pytorch.org/pytorch-certification/"><span class="menu-title-text">PyTorch Certification</span></a></li>
</ul>
</li>
<li id="menu-item-94" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-94"><a href="#" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">Community</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-2299" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-2299"><a href="https://landscape.pytorch.org/"><span class="menu-title-text">Landscape</span></a></li>
	<li id="menu-item-83691" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-83691"><a href="https://pytorch-fdn.github.io/artwork/"><span class="menu-title-text">Logos and Artwork</span></a></li>
	<li id="menu-item-3291" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-3291"><a href="/join-ecosystem"><span class="menu-title-text">Join the Ecosystem</span></a></li>
	<li id="menu-item-3724" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-3724"><a href="https://pytorch.org/community-hub/"><span class="menu-title-text">Community Hub</span></a></li>
	<li id="menu-item-95" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-95"><a href="https://discuss.pytorch.org/"><span class="menu-title-text">Forums</span></a></li>
	<li id="menu-item-2304" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2304"><a href="https://pytorch.org/resources/"><span class="menu-title-text">Developer Resources</span></a></li>
	<li id="menu-item-2209" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2209"><a href="https://pytorch.org/events/"><span class="menu-title-text">Events</span></a></li>
	<li id="menu-item-107198" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-107198"><a href="https://pytorch.org/working-groups/"><span class="menu-title-text">Working Groups</span></a></li>
	<li id="menu-item-6971" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-6971"><a href="https://pytorch.org/meeting-calendar/"><span class="menu-title-text">Meeting Calendar</span></a></li>
	<li id="menu-item-5746" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-5746"><a href="https://pytorch.org/contributor-awards/"><span class="menu-title-text">Contributor Awards</span></a></li>
	<li id="menu-item-3991" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-3991"><a href="https://pytorch.org/programs/ambassadors/"><span class="menu-title-text">Ambassadors</span></a></li>
</ul>
</li>
<li id="menu-item-105" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-105"><a href="https://pytorch.org/projects/" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">Projects</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-3560" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children nectar-regular-menu-item menu-item-3560"><a href="https://pytorch.org/projects/pytorch/" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">PyTorch</span><span class="sf-sub-indicator"><i class="fa fa-angle-right icon-in-menu" aria-hidden="true"></i></span></a>
	<ul class="sub-menu">
		<li id="menu-item-81810" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-81810"><a href="https://pytorch.org/projects/executorch/"><span class="menu-title-text">Executorch</span></a></li>
	</ul>
</li>
	<li id="menu-item-3981" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-3981"><a href="https://pytorch.org/projects/vllm/"><span class="menu-title-text">vLLM</span></a></li>
	<li id="menu-item-3980" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-3980"><a href="https://pytorch.org/projects/deepspeed/"><span class="menu-title-text">DeepSpeed</span></a></li>
	<li id="menu-item-5731" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-5731"><a href="https://pytorch.org/projects/ray/"><span class="menu-title-text">Ray</span></a></li>
	<li id="menu-item-62467" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-62467"><a href="https://pytorch.org/projects/helion/"><span class="menu-title-text">Helion</span></a></li>
	<li id="menu-item-62729" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-62729"><a href="https://pytorch.org/projects/safetensors/"><span class="menu-title-text">Safetensors</span></a></li>
	<li id="menu-item-3573" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-3573"><a href="https://pytorch.org/projects/host-your-project/"><span class="menu-title-text">Host Your Project</span></a></li>
</ul>
</li>
<li id="menu-item-96" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-96"><a href="#" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">Docs</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-97" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-97"><a href="https://pytorch.org/docs/stable/index.html"><span class="menu-title-text">PyTorch</span></a></li>
	<li id="menu-item-2319" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2319"><a href="https://pytorch.org/domains/"><span class="menu-title-text">Domains</span></a></li>
</ul>
</li>
<li id="menu-item-348" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-348"><a href="#" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">Blog &#038; News</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-349" class="menu-item menu-item-type-post_type menu-item-object-page current_page_parent nectar-regular-menu-item menu-item-349"><a href="https://pytorch.org/blog/"><span class="menu-title-text">Blog</span></a></li>
	<li id="menu-item-3420" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-3420"><a href="/announcements"><span class="menu-title-text">Announcements</span></a></li>
	<li id="menu-item-2113" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2113"><a href="https://pytorch.org/case-studies/"><span class="menu-title-text">Case Studies</span></a></li>
	<li id="menu-item-2904" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-2904"><a href="https://pytorch.org/newsletter/"><span class="menu-title-text">Newsletter</span></a></li>
</ul>
</li>
<li id="menu-item-87" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children nectar-regular-menu-item sf-with-ul menu-item-87"><a href="#" aria-haspopup="true" aria-expanded="false"><span class="menu-title-text">About</span><span class="sf-sub-indicator"><i class="fa fa-angle-down icon-in-menu" aria-hidden="true"></i></span></a>
<ul class="sub-menu">
	<li id="menu-item-290" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-290"><a href="https://pytorch.org/foundation/"><span class="menu-title-text">PyTorch Foundation</span></a></li>
	<li id="menu-item-3418" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-3418"><a href="/members"><span class="menu-title-text">Members</span></a></li>
	<li id="menu-item-245" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-245"><a href="https://pytorch.org/governing-board/"><span class="menu-title-text">Governing Board</span></a></li>
	<li id="menu-item-259" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-259"><a href="https://pytorch.org/tac/"><span class="menu-title-text">Technical Advisory Council</span></a></li>
	<li id="menu-item-215" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-215"><a href="https://pytorch.org/credits/"><span class="menu-title-text">Cloud Credit Program</span></a></li>
	<li id="menu-item-277" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-277"><a href="https://pytorch.org/staff/"><span class="menu-title-text">Staff</span></a></li>
	<li id="menu-item-88" class="menu-item menu-item-type-post_type menu-item-object-page nectar-regular-menu-item menu-item-88"><a href="https://pytorch.org/contact/"><span class="menu-title-text">Contact</span></a></li>
	<li id="menu-item-5289" class="menu-item menu-item-type-custom menu-item-object-custom nectar-regular-menu-item menu-item-5289"><a href="https://pytorch.org/wp-content/uploads/2025/09/pytorch_brand_guide_091925a.pdf"><span class="menu-title-text">Brand Guidelines</span></a></li>
</ul>
</li>
<li id="menu-item-135" class="menu-item menu-item-type-post_type menu-item-object-page button_solid_color menu-item-135"><a href="https://pytorch.org/join/"><span class="menu-title-text">JOIN</span></a></li>
							</ul>
													<ul class="buttons sf-menu" data-user-set-ocm="off"><li id="search-btn"><div><a href="#search-box"><span class="icon-salient-search" aria-hidden="true"></span><span class="screen-reader-text">search</span></a></div> </li></ul>
						
					</nav>

					
				</div><!--/span_9-->

				
			</div><!--/row-->
					</div><!--/container-->
	</header>
        
    </div>
        <div id="ajax-content-wrap">

<div class="container-wrap no-sidebar"
     data-midnight="dark"
     data-remove-post-date=""
     data-remove-post-author="0"
     data-remove-post-comment-number="1">

    <div class="container main-content">

        
	  <div class="row heading-title hentry" data-header-style="default_minimal">
		<div class="col span_12 section-title blog-title">
										  <span class="meta-category">

					<a class="announcements" href="https://pytorch.org/blog/category/announcements/">Announcements</a>			  </span>

		  		  <h1 class="entry-title">PyTorch 2.2: FlashAttention-v2 integration, AOTInductor</h1>

						<div id="single-below-header" data-hide-on-mobile="false">
				<span class="meta-author vcard author"><span class="fn"><span class="author-leading">By</span> <a href="#" rel="author">PyTorch Foundation</a></span></span><span class="meta-date date published">January 30, 2024</span><span class="meta-date date updated rich-snippet-hidden">April 30th, 2025</span><span class="meta-comment-count"><a href="https://pytorch.org/blog/pytorch2-2/#respond">No Comments</a></span>			</div><!--/single-below-header-->
				</div><!--/section-title-->
	  </div><!--/row-->

	
        <div class="row">
            
            <div class="post-area col span_12 col_last" role="main">

                
<article id="post-748" class="post-748 post type-post status-publish format-standard category-announcements">
  
  <div class="inner-wrap">

		<div class="post-content" data-hide-featured-media="1">
      
        <div class="content-inner">
<p class="wp-block-paragraph">We are excited to announce the release of PyTorch® 2.2 (<a href="https://github.com/pytorch/pytorch/releases/tag/v2.2.0" target="_blank" rel="noreferrer noopener">release note</a>)! PyTorch 2.2 offers ~2x performance improvements to <em><a href="https://pytorch.org/docs/2.2/generated/torch.nn.functional.scaled_dot_product_attention.html">scaled_dot_product_attention</a></em> via <a href="https://arxiv.org/abs/2307.08691" target="_blank" rel="noreferrer noopener">FlashAttention-v2</a> integration, as well as <em>AOTInductor</em>, a new ahead-of-time compilation and deployment tool built for non-python server-side deployments.</p>



<p class="wp-block-paragraph">This release also includes improved <em>torch.compile</em> support for Optimizers, a number of new inductor optimizations, and a new logging mechanism called TORCH_LOGS.</p>



<p class="wp-block-paragraph">Please note that we are <a href="https://github.com/pytorch/pytorch/issues/114602" target="_blank" rel="noreferrer noopener">deprecating macOS x86 support</a>, and PyTorch 2.2.x will be the last version that supports macOS x64.</p>



<p class="wp-block-paragraph">Along with 2.2, we are also releasing a series of updates to the PyTorch domain libraries. More details can be found in the library updates blog.</p>



<p class="wp-block-paragraph">This release is composed of 3,628 commits and 521 contributors since PyTorch 2.1. We want to sincerely thank our dedicated community for your contributions. As always, we encourage you to try these out and report any issues as we improve 2.2. More information about how to get started with the PyTorch 2-series can be found at our <a href="https://pytorch.org/get-started/pytorch-2.0/">Getting Started</a> page.</p>



<p class="wp-block-paragraph">Summary:</p>



<ul class="wp-block-list">
<li><em><a href="https://pytorch.org/docs/2.2/generated/torch.nn.functional.scaled_dot_product_attention.html">scaled_dot_product_attention</a></em> (SDPA) now supports <em><a href="https://arxiv.org/abs/2307.08691" target="_blank" rel="noreferrer noopener">FlashAttention-2</a></em>, yielding around 2x speedups compared to previous versions.</li>



<li>PyTorch 2.2 introduces a new ahead-of-time extension of <a href="https://dev-discuss.pytorch.org/t/torchinductor-a-pytorch-native-compiler-with-define-by-run-ir-and-symbolic-shapes/747" target="_blank" rel="noreferrer noopener">TorchInductor</a> called <em><a href="https://pytorch.org/docs/main/torch.compiler_aot_inductor.html">AOTInductor</a></em>, designed to compile and deploy PyTorch programs for non-python server-side.</li>



<li><em>torch.distributed</em> supports a new abstraction for initializing and representing ProcessGroups called <em><a href="https://pytorch.org/tutorials/recipes/distributed_device_mesh.html">device_mesh</a></em>.</li>



<li>PyTorch 2.2 ships a standardized, configurable logging mechanism called <a href="https://pytorch.org/tutorials/recipes/torch_logs.html">TORCH_LOGS</a>.</li>



<li>A number of <em>torch.compile</em> improvements are included in PyTorch 2.2, including improved support for compiling Optimizers and improved TorchInductor fusion and layout optimizations.</li>



<li>Please note that we are <a href="https://github.com/pytorch/pytorch/issues/114602" target="_blank" rel="noreferrer noopener">deprecating macOS x86 support</a>, and PyTorch 2.2.x will be the last version that supports macOS x64.</li>
</ul>



<figure class="wp-block-table">
<table class="has-fixed-layout">
<tbody>
<tr>
<td><strong>Stable</strong></td>
<td><strong>Beta</strong></td>
<td><strong>Performance Improvements</strong></td>
</tr>
<tr>
<td> </td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.ok7v7pq0igzw">FlashAttention-2 Integration</a></td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.rk3gf4pgy5m9">Inductor optimizations</a></td>
</tr>
<tr>
<td> </td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.3qfc7y6r1dog">AOTInductor</a></td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.gfep1ccb8bvk">aarch64 optimizations</a></td>
</tr>
<tr>
<td> </td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.n2lkw22a8l2m">TORCH_LOGS</a></td>
<td> </td>
</tr>
<tr>
<td> </td>
<td><em><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.h50nybtt0fdm">device_mesh</a></em></td>
<td> </td>
</tr>
<tr>
<td> </td>
<td><a href="https://pytorch.org/blog/pytorch2-2/#bookmark=id.1lx0dkeu5zqt">Optimizer compilation</a></td>
<td> </td>
</tr>
</tbody>
</table>
</figure>



<p class="wp-block-paragraph">*To see a full list of public feature submissions click <a href="https://docs.google.com/spreadsheets/d/1TzGkWuUMF1yTe88adz1dt2mzbIsZLd3PBasy588VWgk/edit?usp=sharing" target="_blank" rel="noreferrer noopener">here</a>.</p>



<h2 id="beta-features" class="wp-block-heading">Beta Features</h2>



<h3 id="beta-flashattention-2-support-in-torchnnfunctionalscaled_dot_product_attention" class="wp-block-heading">[Beta] FlashAttention-2 support in <em>torch.nn.functional.scaled_dot_product_attention</em></h3>



<p class="wp-block-paragraph"><em><a href="https://pytorch.org/docs/2.2/generated/torch.nn.functional.scaled_dot_product_attention.html">torch.nn.functional.scaled_dot_product_attention</a></em> (SDPA) now supports FlashAttention-2, yielding around 2x speedups (compared to the previous version) and reaching ~50-73% of theoretical maximum FLOPs/s on A100 GPUs.</p>



<p class="wp-block-paragraph">More information is available on FlashAttention-2 in <a href="https://arxiv.org/abs/2307.08691" target="_blank" rel="noreferrer noopener">this paper</a>.</p>



<p class="wp-block-paragraph">For a tutorial on how to use SDPA please see <a href="https://pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html">this tutorial</a>.</p>



<h3 id="beta-aotinductor-ahead-of-time-compilation-and-deployment-for-torchexport-ed-programs" class="wp-block-heading">[Beta] AOTInductor: ahead-of-time compilation and deployment for torch.export-ed programs</h3>



<p class="wp-block-paragraph">AOTInductor is an extension of <a href="https://dev-discuss.pytorch.org/t/torchinductor-a-pytorch-native-compiler-with-define-by-run-ir-and-symbolic-shapes/747" target="_blank" rel="noreferrer noopener">TorchInductor</a>, designed to process exported PyTorch models, optimize them, and produce shared libraries as well as other relevant artifacts. These compiled artifacts can be deployed in non-Python environments, which are frequently employed for inference on the server-side. Note that AOTInductor supports the same backends as Inductor, including CUDA, ROCm, and CPU.</p>



<p class="wp-block-paragraph">For more information please see the <a href="https://pytorch.org/docs/main/torch.compiler_aot_inductor.html">AOTInductor tutorial</a>.</p>



<h3 id="beta-fine-grained-configurable-logging-via-torch_logs" class="wp-block-heading">[Beta] Fine-grained configurable logging via TORCH_LOGS</h3>



<p class="wp-block-paragraph">PyTorch now ships a standardized, configurable logging mechanism that can be used to analyze the status of various subsystems such as compilation and distributed operations.</p>



<p class="wp-block-paragraph">Logs can be enabled via the TORCH_LOGS environment variable. For example, to set the log level of TorchDynamo to logging.ERROR and the log level of TorchInductor to logging.DEBUG pass <em>TORCH_LOGS=”-dynamo,+inductor”</em> to PyTorch.</p>



<p class="wp-block-paragraph">For more information, please see the logging <a href="https://pytorch.org/docs/2.2/logging.html">documentation</a> and <a href="https://pytorch.org/tutorials/recipes/torch_logs.html">tutorial</a>.</p>



<h3 id="beta-torchdistributeddevice_mesh" class="wp-block-heading">[Beta] torch.distributed.device_mesh</h3>



<p class="wp-block-paragraph">PyTorch 2.2 introduces a new abstraction for representing the ProcessGroups involved in distributed parallelisms called <em>torch.distributed.device_mesh</em>. This abstraction allows users to represent inter-node and intra-node process groups via an N-dimensional array where, for example, one dimension can data parallelism in FSDP while another could represent tensor parallelism within FSDP.</p>



<p class="wp-block-paragraph">For more information, see the <a href="https://pytorch.org/tutorials/recipes/distributed_device_mesh.html">device_mesh tutorial</a>.</p>



<h3 id="beta-improvements-to-torchcompile-ing-optimizers" class="wp-block-heading">[Beta] Improvements to <em>torch.compile</em>-ing Optimizers</h3>



<p class="wp-block-paragraph">A number of improvements have been made to torch.compile-ing Optimizers including less overhead and support for cuda graphs.</p>



<p class="wp-block-paragraph">More technical details of the improvements are available on <a href="https://dev-discuss.pytorch.org/t/compiling-the-optimizer-with-pt2/1669" target="_blank" rel="noreferrer noopener">dev-discuss</a>, and a recipe for <em>torch.compile</em>-ing optimizers is available <a href="https://pytorch.org/tutorials/recipes/compiling_optimizer.html">here</a>.</p>



<h2 id="performance-improvements" class="wp-block-heading">Performance Improvements</h2>



<h3 id="inductor-performance-optimizations" class="wp-block-heading">Inductor Performance Optimizations</h3>



<p class="wp-block-paragraph">A number of performance optimizations have been added to TorchInductor including <a href="https://github.com/pytorch/pytorch/pull/111437" target="_blank" rel="noreferrer noopener">horizontal fusion support for torch.concat</a>, <a href="https://github.com/pytorch/pytorch/pull/114600" target="_blank" rel="noreferrer noopener">improved convolution layout optimizations</a>, and improved <em>scaled_dot_product_attention</em> <a href="https://github.com/pytorch/pytorch/pull/109156" target="_blank" rel="noreferrer noopener">pattern</a> <a href="https://github.com/pytorch/pytorch/pull/110001" target="_blank" rel="noreferrer noopener">matching</a>.</p>



<p class="wp-block-paragraph">For a complete list of inductor optimizations, please see the <a href="https://github.com/pytorch/pytorch/tree/v2.2.0" target="_blank" rel="noreferrer noopener">Release Notes</a>.</p>



<h3 id="aarch64-performance-optimizations" class="wp-block-heading">aarch64 Performance Optimizations</h3>



<p class="wp-block-paragraph">PyTorch 2.2 includes a number of performance enhancements for aarch64 including support for <a href="https://github.com/pytorch/pytorch/pull/115037/files" target="_blank" rel="noreferrer noopener">mkldnn weight pre-packing</a>, improved <a href="https://github.com/intel/ideep" target="_blank" rel="noreferrer noopener">ideep</a> <a href="https://github.com/intel/ideep/pull/261" target="_blank" rel="noreferrer noopener">primitive caching</a>, and improved inference speed via <a href="https://github.com/oneapi-src/oneDNN/pull/1590" target="_blank" rel="noreferrer noopener">fixed format kernel improvements</a> to <a href="https://github.com/oneapi-src/oneDNN/" target="_blank" rel="noreferrer noopener">OneDNN</a>.</p>



<p class="wp-block-paragraph">For a complete list of aarch64 optimizations, please see the <a href="https://github.com/pytorch/pytorch/tree/v2.2.0" target="_blank" rel="noreferrer noopener">Release Notes</a>.</p>



<p class="wp-block-paragraph">&nbsp;</p>
</div>        
      </div><!--/post-content-->
      
    </div><!--/inner-wrap-->
    
</article>
            </div><!--/post-area-->

            
        </div><!--/row-->

        <div class="row">
            
            <div class="comments-section"
                 data-author-bio="false">
                
<div class="comment-wrap " data-midnight="dark" data-comments-open="false">


			<!-- If comments are closed. -->
		<!--<p class="nocomments">Comments are closed.</p>-->

	


</div>            </div>

        </div><!--/row-->

    </div><!--/container main-content-->

    <div class="nectar-global-section before-footer" role="contentinfo"><div class="container normal-container row">
		<div id="fws_6a36a861dddf1"  data-column-margin="default" data-midnight="light" data-top-percent="3%" data-bottom-percent="3%"  class="wpb_row vc_row-fluid vc_row full-width-section has-row-bg-color  top_padding_phone_7pct bottom_padding_phone_7pct"  style="padding-top: calc(100vw * 0.03); padding-bottom: calc(100vw * 0.03); --row-bg-color: #333333;"><div class="row-bg-wrap" data-bg-animation="none" data-bg-animation-delay="" data-bg-overlay="false"><div class="inner-wrap row-bg-layer" ><div class="row-bg viewport-desktop using-bg-color"  style="background-color: #333333; "></div></div></div><div class="row_col_wrap_12 col span_12 light left">
	<div  class="vc_col-sm-4 wpb_column column_container vc_column_container col no-extra-padding inherit_tablet inherit_phone "  data-padding-pos="all" data-has-bg-color="false" data-bg-color="" data-bg-opacity="1" data-animation="" data-delay="0" >
		<div class="vc_column-inner" >
			<div class="wpb_wrapper">
				
<div class="wpb_text_column wpb_content_element " >
	<h3>Docs</h3>
<p>Access comprehensive developer documentation for PyTorch</p>
<p><span style="color: #ee4c2c;"><a style="color: #ee4c2c;" href="/docs">View Docs ›</a></span></p>
</div>




			</div> 
		</div>
	</div> 

	<div  class="vc_col-sm-4 wpb_column column_container vc_column_container col no-extra-padding inherit_tablet inherit_phone "  data-padding-pos="all" data-has-bg-color="false" data-bg-color="" data-bg-opacity="1" data-animation="" data-delay="0" >
		<div class="vc_column-inner" >
			<div class="wpb_wrapper">
				
<div class="wpb_text_column wpb_content_element " >
	<h3>Tutorials</h3>
<p>Get in-depth tutorials for beginners and advanced developers</p>
<p><span style="color: #ee4c2c;"><a style="color: #ee4c2c;" href="/tutorials">View Tutorials ›</a></span></p>
</div>




			</div> 
		</div>
	</div> 

	<div  class="vc_col-sm-4 wpb_column column_container vc_column_container col no-extra-padding inherit_tablet inherit_phone "  data-padding-pos="all" data-has-bg-color="false" data-bg-color="" data-bg-opacity="1" data-animation="" data-delay="0" >
		<div class="vc_column-inner" >
			<div class="wpb_wrapper">
				
<div class="wpb_text_column wpb_content_element " >
	<h3>Resources</h3>
<p>Find development resources and get your questions answered</p>
<p><span style="color: #ee4c2c;"><a style="color: #ee4c2c;" href="/resources">View Resources ›</a></span></p>
</div>




			</div> 
		</div>
	</div> 
</div></div>
		<div id="fws_6a36a861de663"  data-column-margin="default" data-midnight="light"  class="wpb_row vc_row-fluid vc_row full-width-section has-row-bg-color"  style="padding-top: 60px; padding-bottom: 60px; --row-bg-color: #000000;"><div class="row-bg-wrap" data-bg-animation="none" data-bg-animation-delay="" data-bg-overlay="false"><div class="inner-wrap row-bg-layer" ><div class="row-bg viewport-desktop using-bg-color"  style="background-color: #000000; "></div></div></div><div class="row_col_wrap_12 col span_12 light left">
	<div  class="vc_col-sm-12 wpb_column column_container vc_column_container col no-extra-padding inherit_tablet inherit_phone "  data-padding-pos="all" data-has-bg-color="false" data-bg-color="" data-bg-opacity="1" data-animation="" data-delay="0" >
		<div class="vc_column-inner" >
			<div class="wpb_wrapper">
				
<div class="wpb_text_column wpb_content_element " >
	<h2><strong>Stay in touch</strong> for updates, event info, and the latest news</h2>
</div>




	<div class="wpb_raw_code wpb_raw_html wpb_content_element" >
		<div class="wpb_wrapper">
			        <script charset="utf-8" type="text/javascript" src="//js.hsforms.net/forms/embed/v2.js"></script>
        <script type="text/javascript" nonce="a612bd30df">
          hbspt.forms.create({
            region: "na1",
            portalId: "8112310",
            formId: "2fb2231c-000b-4ec5-88a0-1ab242549c9e"
          });
        </script>
		</div>
	</div>

<div class="wpb_text_column wpb_content_element " >
	<p><span style="color: #777777; font-size: .8em;">By submitting this form, I consent to receive marketing emails from the LF and its projects regarding their events, training, research, developments, and related announcements. I understand that I can unsubscribe at any time using the links in the footers of the emails I receive. <a style="color: #777777;" href="https://www.linuxfoundation.org/privacy/">Privacy Policy</a>.</span></p>
</div>




			</div> 
		</div>
	</div> 
</div></div>
</div></div>
</div><!--/container-wrap-->


<div id="footer-outer" data-midnight="light" data-cols="1" data-custom-color="true" data-disable-copyright="false" data-matching-section-color="true" data-copyright-line="false" data-using-bg-img="false" data-bg-img-overlay="0.8" data-full-width="false" data-using-widget-area="true" data-link-hover="default"role="contentinfo">
	
		
	<div id="footer-widgets" data-has-widgets="false" data-cols="1">
		
		<div class="container">
			
						
			<div class="row">
				
								
				<div class="col span_12">
												<div class="widget">			
							</div>
											</div>
					
											
						
													
															
							</div>
													</div><!--/container-->
					</div><!--/footer-widgets-->
					
					
  <div class="row" id="copyright" data-layout="default">

	<div class="container">

		
	  <div class="col span_7 col_last">
      <ul class="social">
        <li><a target="_blank" rel="noopener" href="https://twitter.com/pytorch"><span class="screen-reader-text">x-twitter</span><i class="icon-salient-x-twitter" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://www.facebook.com/pytorch"><span class="screen-reader-text">facebook</span><i class="fa fa-facebook" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://www.linkedin.com/company/pytorch"><span class="screen-reader-text">linkedin</span><i class="fa fa-linkedin" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://www.youtube.com/pytorch"><span class="screen-reader-text">youtube</span><i class="fa fa-youtube-play" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://github.com/pytorch/pytorch"><span class="screen-reader-text">github</span><i class="fa fa-github-alt" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://join.slack.com/t/pytorch/shared_invite/zt-2j2la612p-miUinTTaxXczKOJw48poHA"><span class="screen-reader-text">slack</span><i class="fa fa-slack" aria-hidden="true"></i></a></li><li><a target="_blank" rel="noopener" href="https://discord.com/invite/eNSRmh92XT"><span class="screen-reader-text">discord</span><i class="icon-salient-discord" aria-hidden="true"></i></a></li>      </ul>
	  </div><!--/span_7-->

	  		<div class="col span_5">
						<div class="widget"></div>
		<p>&copy; 2026 PyTorch. Copyright © The Linux Foundation®. All rights reserved. The Linux Foundation has registered trademarks and uses trademarks. For more information, including terms of use, privacy policy, and trademark usage, please see our <a href="https://www.linuxfoundation.org/legal/policies">Policies</a> page. <a href="https://www.linuxfoundation.org/trademark-usage">Trademark Usage</a>. <a href="http://www.linuxfoundation.org/privacy">Privacy Policy</a>.</p>		</div><!--/span_5-->
		
	</div><!--/container-->
  </div><!--/row-->
		
</div><!--/footer-outer-->


	<div id="slide-out-widget-area-bg" class="slide-out-from-right-hover dark">
				</div>

		<div id="slide-out-widget-area" role="dialog" aria-modal="true" aria-label="Off Canvas Menu" class="slide-out-from-right-hover" data-dropdown-func="separate-dropdown-parent-link" data-back-txt="Back">

			<div class="inner-wrap">
			<div class="inner" data-prepend-menu-mobile="false">

				<a class="slide_out_area_close" href="#"><span class="screen-reader-text">Close Menu</span>
					<span class="icon-salient-x icon-default-style"></span>				</a>


									<div class="off-canvas-menu-container mobile-only" role="navigation">

						
						<ul class="menu">
							<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-89"><a href="#" aria-haspopup="true" aria-expanded="false">Learn</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2296"><a href="https://pytorch.org/get-started/locally/">Get Started</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-90"><a href="https://pytorch.org/tutorials/">Tutorials</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-91"><a href="https://pytorch.org/tutorials/beginner/basics/intro.html">Learn the Basics</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-92"><a href="https://docs.pytorch.org/tutorials/recipes_index.html">PyTorch Recipes</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-93"><a href="https://pytorch.org/tutorials/beginner/introyt.html">Intro to PyTorch &#8211; YouTube Series</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2200"><a href="https://pytorch.org/webinars/">Webinars</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-113097"><a href="https://pytorch.org/pytorch-certification/">PyTorch Certification</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-94"><a href="#" aria-haspopup="true" aria-expanded="false">Community</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-2299"><a href="https://landscape.pytorch.org/">Landscape</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-83691"><a href="https://pytorch-fdn.github.io/artwork/">Logos and Artwork</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-3291"><a href="/join-ecosystem">Join the Ecosystem</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-3724"><a href="https://pytorch.org/community-hub/">Community Hub</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-95"><a href="https://discuss.pytorch.org/">Forums</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2304"><a href="https://pytorch.org/resources/">Developer Resources</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2209"><a href="https://pytorch.org/events/">Events</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-107198"><a href="https://pytorch.org/working-groups/">Working Groups</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-6971"><a href="https://pytorch.org/meeting-calendar/">Meeting Calendar</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-5746"><a href="https://pytorch.org/contributor-awards/">Contributor Awards</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-3991"><a href="https://pytorch.org/programs/ambassadors/">Ambassadors</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-105"><a href="https://pytorch.org/projects/" aria-haspopup="true" aria-expanded="false">Projects</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-3560"><a href="https://pytorch.org/projects/pytorch/" aria-haspopup="true" aria-expanded="false">PyTorch</a>
	<ul class="sub-menu">
		<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-81810"><a href="https://pytorch.org/projects/executorch/">Executorch</a></li>
	</ul>
</li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-3981"><a href="https://pytorch.org/projects/vllm/">vLLM</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-3980"><a href="https://pytorch.org/projects/deepspeed/">DeepSpeed</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-5731"><a href="https://pytorch.org/projects/ray/">Ray</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-62467"><a href="https://pytorch.org/projects/helion/">Helion</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-62729"><a href="https://pytorch.org/projects/safetensors/">Safetensors</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-3573"><a href="https://pytorch.org/projects/host-your-project/">Host Your Project</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-96"><a href="#" aria-haspopup="true" aria-expanded="false">Docs</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-97"><a href="https://pytorch.org/docs/stable/index.html">PyTorch</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2319"><a href="https://pytorch.org/domains/">Domains</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-348"><a href="#" aria-haspopup="true" aria-expanded="false">Blog &#038; News</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-post_type menu-item-object-page current_page_parent menu-item-349"><a href="https://pytorch.org/blog/">Blog</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-3420"><a href="/announcements">Announcements</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2113"><a href="https://pytorch.org/case-studies/">Case Studies</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2904"><a href="https://pytorch.org/newsletter/">Newsletter</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-87"><a href="#" aria-haspopup="true" aria-expanded="false">About</a>
<ul class="sub-menu">
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-290"><a href="https://pytorch.org/foundation/">PyTorch Foundation</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-3418"><a href="/members">Members</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-245"><a href="https://pytorch.org/governing-board/">Governing Board</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-259"><a href="https://pytorch.org/tac/">Technical Advisory Council</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-215"><a href="https://pytorch.org/credits/">Cloud Credit Program</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-277"><a href="https://pytorch.org/staff/">Staff</a></li>
	<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-88"><a href="https://pytorch.org/contact/">Contact</a></li>
	<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-5289"><a href="https://pytorch.org/wp-content/uploads/2025/09/pytorch_brand_guide_091925a.pdf">Brand Guidelines</a></li>
</ul>
</li>
<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-135"><a href="https://pytorch.org/join/">JOIN</a></li>

						</ul>

						<ul class="menu secondary-header-items">
													</ul>
					</div>
					
				</div>

				<div class="bottom-meta-wrap"></div><!--/bottom-meta-wrap--></div> <!--/inner-wrap-->
				</div>
		
</div> <!--/ajax-content-wrap-->

	<a id="to-top" aria-label="Back to top" role="button" href="#" class="mobile-disabled"><i role="presentation" class="fa fa-angle-up"></i></a>
	<script type="speculationrules">
{"prefetch":[{"source":"document","where":{"and":[{"href_matches":"/*"},{"not":{"href_matches":["/wp-*.php","/wp-admin/*","/wp-content/uploads/*","/wp-content/*","/wp-content/plugins/*","/wp-content/themes/salient-child/*","/wp-content/themes/salient/*","/*\\?(.+)"]}},{"not":{"selector_matches":"a[rel~=\"nofollow\"]"}},{"not":{"selector_matches":".no-prefetch, .no-prefetch a"}}]},"eagerness":"conservative"}]}
</script>
<script type="text/javascript" nonce="a612bd30df"> /* <![CDATA[ */var tribe_l10n_datatables = {"aria":{"sort_ascending":": activate to sort column ascending","sort_descending":": activate to sort column descending"},"length_menu":"Show _MENU_ entries","empty_table":"No data available in table","info":"Showing _START_ to _END_ of _TOTAL_ entries","info_empty":"Showing 0 to 0 of 0 entries","info_filtered":"(filtered from _MAX_ total entries)","zero_records":"No matching records found","search":"Search:","all_selected_text":"All items on this page were selected. ","select_all_link":"Select all pages","clear_selection":"Clear Selection.","pagination":{"all":"All","next":"Next","previous":"Previous"},"select":{"rows":{"0":"","_":": Selected %d rows","1":": Selected 1 row"}},"datepicker":{"dayNames":["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"dayNamesShort":["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],"dayNamesMin":["S","M","T","W","T","F","S"],"monthNames":["January","February","March","April","May","June","July","August","September","October","November","December"],"monthNamesShort":["January","February","March","April","May","June","July","August","September","October","November","December"],"monthNamesMin":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"nextText":"Next","prevText":"Prev","currentText":"Today","closeText":"Done","today":"Today","clear":"Clear"}};/* ]]> */ </script><script id="wpb-modifications"> window.wpbCustomElement = 1; </script><script id="tec-user-agent-js" src="https://pytorch.org/wp-content/plugins/the-events-calendar/common/build/js/user-agent.js?ver=da75d0bdea6dde3898df"></script>
<script id="salient-child-featherlight-script-js" src="https://pytorch.org/wp-content/themes/salient-child/vc-addons/js/featherlight.js?ver=3.6.1"></script>
<script id="jquery-ui-core-js" src="https://pytorch.org/wp-includes/js/jquery/ui/core.min.js?ver=1.13.3"></script>
<script id="jquery-ui-datepicker-js" src="https://pytorch.org/wp-includes/js/jquery/ui/datepicker.min.js?ver=1.13.3"></script>
<script id="jquery-ui-datepicker-js-after">
jQuery(function(jQuery){jQuery.datepicker.setDefaults({"closeText":"Close","currentText":"Today","monthNames":["January","February","March","April","May","June","July","August","September","October","November","December"],"monthNamesShort":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"nextText":"Next","prevText":"Previous","dayNames":["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"dayNamesShort":["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],"dayNamesMin":["S","M","T","W","T","F","S"],"dateFormat":"MM d, yy","firstDay":1,"isRTL":false});});
//# sourceURL=jquery-ui-datepicker-js-after
</script>
<script id="salient-child-javascript-js" src="https://pytorch.org/wp-content/themes/salient-child/javascript.js?ver=3.6.1"></script>
<script id="jquery-easing-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/jquery.easing.min.js?ver=1.3"></script>
<script id="nectar_priority-js" src="https://pytorch.org/wp-content/themes/salient/js/build/priority.js?ver=18.1.1"></script>
<script id="nectar-transit-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/transit.min.js?ver=0.9.9"></script>
<script id="nectar-waypoints-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/waypoints.js?ver=4.0.2"></script>
<script id="imagesLoaded-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/imagesLoaded.min.js?ver=4.1.4"></script>
<script id="hoverintent-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/hoverintent.min.js?ver=1.9"></script>
<script id="fancyBox-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/jquery.fancybox.js?ver=18.1.1"></script>
<script id="anime-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/anime.min.js?ver=4.5.1"></script>
<script id="superfish-js" src="https://pytorch.org/wp-content/themes/salient/js/build/third-party/superfish.js?ver=1.5.8"></script>
<script id="nectar-frontend-js-extra">
var nectarLove = {"ajaxurl":"https://pytorch.org/wp-admin/admin-ajax.php","postID":"748","rooturl":"https://pytorch.org","disqusComments":"false","loveNonce":"3caeac3b45","mapApiKey":""};
var nectarOptions = {"delay_js":"false","smooth_scroll":"false","smooth_scroll_strength":"50","quick_search":"false","react_compat":"disabled","header_entrance":"false","body_border_func":"default","disable_box_roll_mobile":"false","body_border_mobile":"0","dropdown_hover_intent":"default","simplify_ocm_mobile":"0","mobile_header_format":"centered-menu","ocm_btn_position":"default","left_header_dropdown_func":"default","ajax_add_to_cart":"0","ocm_remove_ext_menu_items":"remove_images","woo_product_filter_toggle":"0","woo_sidebar_toggles":"true","woo_sticky_sidebar":"0","woo_minimal_product_hover":"default","woo_minimal_product_effect":"default","woo_related_upsell_carousel":"false","woo_product_variable_select":"default","woo_using_cart_addons":"false","view_transitions_effect":""};
var nectar_front_i18n = {"menu":"Menu","next":"Next","previous":"Previous","close":"Close"};
//# sourceURL=nectar-frontend-js-extra
</script>
<script id="nectar-frontend-js" src="https://pytorch.org/wp-content/themes/salient/js/build/init.js?ver=18.1.1"></script>
<script id="touchswipe-js" src="https://pytorch.org/wp-content/plugins/salient-core/js/third-party/touchswipe.min.js?ver=3.1.4"></script>
<script id="prism-scripts-js" src="https://pytorch.org/wp-content/themes/salient-child/vc-addons/js/prism.js?ver=18.1.1"></script>
<script id="wpb_composer_front_js-js" src="https://pytorch.org/wp-content/plugins/js_composer_salient/assets/js/dist/js_composer_front.min.js?ver=8.7.2"></script>
<script id="wp-emoji-settings" type="application/json">
{"baseUrl":"https://s.w.org/images/core/emoji/17.0.2/72x72/","ext":".png","svgUrl":"https://s.w.org/images/core/emoji/17.0.2/svg/","svgExt":".svg","source":{"concatemoji":"https://pytorch.org/wp-includes/js/wp-emoji-release.min.js?ver=7.0"}}
</script>
<script type="module">
/*! This file is auto-generated */
const a=JSON.parse(document.getElementById("wp-emoji-settings").textContent),o=(window._wpemojiSettings=a,"wpEmojiSettingsSupports"),s=["flag","emoji"];function i(e){try{var t={supportTests:e,timestamp:(new Date).valueOf()};sessionStorage.setItem(o,JSON.stringify(t))}catch(e){}}function c(e,t,n){e.clearRect(0,0,e.canvas.width,e.canvas.height),e.fillText(t,0,0);t=new Uint32Array(e.getImageData(0,0,e.canvas.width,e.canvas.height).data);e.clearRect(0,0,e.canvas.width,e.canvas.height),e.fillText(n,0,0);const a=new Uint32Array(e.getImageData(0,0,e.canvas.width,e.canvas.height).data);return t.every((e,t)=>e===a[t])}function p(e,t){e.clearRect(0,0,e.canvas.width,e.canvas.height),e.fillText(t,0,0);var n=e.getImageData(16,16,1,1);for(let e=0;e<n.data.length;e++)if(0!==n.data[e])return!1;return!0}function u(e,t,n,a){switch(t){case"flag":return n(e,"\ud83c\udff3\ufe0f\u200d\u26a7\ufe0f","\ud83c\udff3\ufe0f\u200b\u26a7\ufe0f")?!1:!n(e,"\ud83c\udde8\ud83c\uddf6","\ud83c\udde8\u200b\ud83c\uddf6")&&!n(e,"\ud83c\udff4\udb40\udc67\udb40\udc62\udb40\udc65\udb40\udc6e\udb40\udc67\udb40\udc7f","\ud83c\udff4\u200b\udb40\udc67\u200b\udb40\udc62\u200b\udb40\udc65\u200b\udb40\udc6e\u200b\udb40\udc67\u200b\udb40\udc7f");case"emoji":return!a(e,"\ud83e\u1fac8")}return!1}function f(e,t,n,a){let r;const o=(r="undefined"!=typeof WorkerGlobalScope&&self instanceof WorkerGlobalScope?new OffscreenCanvas(300,150):document.createElement("canvas")).getContext("2d",{willReadFrequently:!0}),s=(o.textBaseline="top",o.font="600 32px Arial",{});return e.forEach(e=>{s[e]=t(o,e,n,a)}),s}function r(e){var t=document.createElement("script");t.src=e,t.defer=!0,document.head.appendChild(t)}a.supports={everything:!0,everythingExceptFlag:!0},new Promise(t=>{let n=function(){try{var e=JSON.parse(sessionStorage.getItem(o));if("object"==typeof e&&"number"==typeof e.timestamp&&(new Date).valueOf()<e.timestamp+604800&&"object"==typeof e.supportTests)return e.supportTests}catch(e){}return null}();if(!n){if("undefined"!=typeof Worker&&"undefined"!=typeof OffscreenCanvas&&"undefined"!=typeof URL&&URL.createObjectURL&&"undefined"!=typeof Blob)try{var e="postMessage("+f.toString()+"("+[JSON.stringify(s),u.toString(),c.toString(),p.toString()].join(",")+"));",a=new Blob([e],{type:"text/javascript"});const r=new Worker(URL.createObjectURL(a),{name:"wpTestEmojiSupports"});return void(r.onmessage=e=>{i(n=e.data),r.terminate(),t(n)})}catch(e){}i(n=f(s,u,c,p))}t(n)}).then(e=>{for(const n in e)a.supports[n]=e[n],a.supports.everything=a.supports.everything&&a.supports[n],"flag"!==n&&(a.supports.everythingExceptFlag=a.supports.everythingExceptFlag&&a.supports[n]);var t;a.supports.everythingExceptFlag=a.supports.everythingExceptFlag&&!a.supports.flag,a.supports.everything||((t=a.source||{}).concatemoji?r(t.concatemoji):t.wpemoji&&t.twemoji&&(r(t.twemoji),r(t.wpemoji)))});
//# sourceURL=https://pytorch.org/wp-includes/js/wp-emoji-loader.min.js
</script>
<script type="text/javascript" nonce="a612bd30df"></script></body>
</html>