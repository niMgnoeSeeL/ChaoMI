We appreciate the reviewers for their valuable comments and feedback. Here is a summary of the issues raised and our responses:

[Summary]

-Why not compare with the symbolic execution (SE)/model-counting (MC) based approach?(R2,R3)

Indeed, it is reasonable to compare the proposed approach with the SE/MC-based approach. Each approach has its own strengths and limitations of scalability. In the camera-ready version, we will include such a comparison. Please see the detailed response in the following section. This work focuses on the statistical approach and its limitations with a small sample size.

-Can the proposed approach be applicable to the realistic security domain?(R2,R3)

Additional experiments on a stream cipher, similar to LeakWatch, demonstrate the applicability of our approach in a realistic security domain. Please see the detailed response in the following section. The results will be included in the camera-ready version.

-What is the impact of the overestimation?(R1)

The overestimation of the MI can lead to a false sense of insecurity, which may induce unnecessary security countermeasures. We will include this in the camera-ready version.

-Can the theoretical explanation of the proposed method be strengthened?(R1)

We commit to strengthening the theoretical explanation and proof in the camera-ready version.

-Isn't the statistical method both over and under-estimate the MI?(R3)

Indeed, the statistical method can both over or under-estimate the MI. What we described in Section 2.2 is that, when the sample size is small, Miller's method may underestimate the MI, i.e., giving a false sense of safety, which is demonstrated in the experiment. We will clarify this point in the camera-ready version.

-Does the intuition behind Chao's estimation that the number of undetected events is close to the number of detected rare events hold for <secret,observable> pairs?(R2)

Yes. The intuition behind Chao's estimation that the number of undetected events is close to the number of singleton events comes from Chao's inequality (Chao, 1984), which estimates the lower bound of the number of undetected events. Throughout our experiments, we observed it mostly holds for <secret,observable> pairs.

[Comparison with SE/MC-based approach]

SE/MC-based approaches are the mainstream for information leakage testing; recent works demonstrated that they can be scalable for large-scale systems either independently or in conjunction with statistical methods (Saha, 2023; Bao, 2021). Thus, we want to clarify that our claim does not argue that the statistical approach is always better than the SE/MC-based approach in all scalability issues.

Both SE/MC-based and statistical approaches possess distinct strengths and scalability limitations. SE/MC-based methods may prove inaccurate or infeasible for certain systems due to operations beyond the scope of SE or MC tools, such as invoking external scripts or system calls, file reading, or network packet retrieval (e.g., `int val=call("./return-3.sh");`). In such cases, the language-agnostic statistical approach excels in handling these challenges.

The primary constraint of the statistical method lies in sample size limitations. Current statistical methods yield inaccurate or unsafe outcomes with small sample sizes, the central focus of our work. To address this, we propose a novel biostatistical approach to estimate mutual information with small samples. We believe our contribution extends beyond statistical methods, enhancing general information leakage testing by seamlessly integrating with SE/MC-based approaches.

[Representative Subject for the Realistic Security Domain]

To showcase the applicability of our approach in a realistic security domain, we conducted an experiment on a stream cipher, akin to LeakWatch. This experiment gauges the mutual information (MI) between the bit-flip event (secret) and the cipher system's output (observable) for each bit of the internal state to analyze 1) which bits of its internal state are leaked to the output, and 2) how is the cipher system working; from the pattern of the MI, one can infer which sets of bits undergo the same operations (for more details, please check Sec.6.2. in the LeakWatch paper).

The cipher, resembling Crypto-1, operators on a half-byte (nibble, 4 bits) and has a 96-bit state.
-The state of the cipher system $s=(s_0,s_1,...,s_{23})$, where each $s_i$ is 4-bit.
-The output of the cipher system $o=f(s)=f_c(f_a(s_4,s_5,s_6,s_7),f_b(s_8,s_9,s_{10},s_{11}),f_b(s_{12},s_{13},s_{14},s_{15}),f_a(s_{16},s_{17},s_{18},s_{19}),f_b(s_{20},s_{21},s_{22},s_{23}))$, where
  -$f_a(a,b,c,d)=((a\lor~b)\oplus~(a\land~d))\oplus~(c\land~((a\oplus~b)\lor~d))$
  -$f_b(a,b,c,d)=((a\land~b)\lor~c)\oplus~((a\oplus~b)\land~(c\lor~d))$
  -$f_c(a,b,c,d,e)=((((a\oplus~b)\oplus~c)\oplus~d)\oplus~e)$
  -$x\land~y:=xy\bmod16$, $x\lor~y:=x^{y+1}\bmod16$, $x\oplus~y:=x+y\bmod16$

We get the ground truth MI from 10K samples; it shows non-leakage of the first four nibbles (MI$=0$), and its pattern shows each of $\{(s_4,s_5,s_6,s_7),(s_{16},s_{17},s_{18},s_{19})\}$ and $\{(s_8,s_9,s_{10},s_{11}),(s_{12},s_{13},s_{14},s_{15}),(s_{20},s_{21},s_{22},s_{23})\}$ undergo the same operations $f_a$ and $f_b$, respectively. Then, subsets of samples $n=\rm10,20,50,100,200,500,1000,2000,5000$ are employed to estimate the MI using Empirical, Miller, and ChaoSRM estimators. We found that when the sample size is insufficient,

1. Empirical has the largest error,
2. Miller falsely indicates non-leakage for more nibbles at $n<500$, Empirical and ChaoSRM yield correct results, and
3. ChaoSRM reveals the operation pattern at $n\geq200$, while Empirical and Miller need $n\geq1000$.

This experiment demonstrates our approach's safe and accurate MI estimation with a small sample size in a realistic security domain. Additional experiments for different cipher systems can be included in the camera-ready version if necessary.
