
/*
in vec2 UV;
out vec3 color;

*/

uniform float logarithmic;

uniform sampler2D spectrogram;

void main()
{
    vec4 color;

    if (logarithmic > 0.0)
        color = texture2D(spectrogram, vec2(gl_TexCoord[0].s,
            exp2(gl_TexCoord[0].t) * 0.5 - 1.0));
    else
        color = texture2D(spectrogram, gl_TexCoord[0].st);

    gl_FragColor = color;
}

