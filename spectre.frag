
/*
in vec2 UV;
out vec3 color;

*/

uniform float logarithmic;
uniform float volume;

uniform sampler2D spectrogram;

const float grid = 0.0;

void main()
{
    vec2 tcoord;

    
    /*
     * max = 22100.0
     * upper = 11050
     * lower = 30Hz -> log(30) / log(upper)
     * lower_min = 1 - lower
     */
    if (logarithmic > 0.0) {
        tcoord.s = gl_TexCoord[0].s;
        /* t_new = pow(upper, t * lower + lower_min) / max */
        tcoord.t = pow(22100.0, gl_TexCoord[0].t * 0.59 + 0.41) / 22100.0;
    } else
        tcoord.st = gl_TexCoord[0].st;

    if (grid > 0.0) {
        if (tcoord.t > 0.00452 && mod(log2(tcoord.t * 22100.0), 1.00) < .4)
            gl_FragColor = vec4(0.2, 0.4, 0.8, 1.0);
        else
            gl_FragColor = texture2D(spectrogram, tcoord);
    } else
        if (volume > 0.0)
            gl_FragColor = log2(texture2D(spectrogram, tcoord) * 32.0 + 1.0) / 5.0;
        else
            gl_FragColor = texture2D(spectrogram, tcoord);

    return;
}

