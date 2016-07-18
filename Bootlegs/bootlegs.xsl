<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="Data">
        <html>
            <head>
                <link rel="stylesheet" type="text/css">
                    <xsl:attribute name="href"><xsl:value-of select="@css"/></xsl:attribute>
                </link>
                <title>Pearl Jam Bootlegs</title>
            </head>
            <body>
                <div>
                    <p class="css-validator">
                        <a href="http://jigsaw.w3.org/css-validator/check/referer">
                            <img class="css-validator" src="http://jigsaw.w3.org/css-validator/images/vcss" alt="Valid CSS!"/>
                        </a>
                    </p>
                    <p class="top">My&#xA0;&#xA0;Pearl Jam&#xA0;&#xA0;Bootlegs</p>
                    <p class="who">by Xavier</p>
                    <xsl:apply-templates/>
                </div>
                <p class="timestamp">
                    <xsl:value-of select="concat('Dernière mise à jour : ',@update)"/>
                </p>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="Series">
        <h2 class="year"><xsl:value-of select="@year"/>&#xA0;&#xA0;Bootlegs</h2>
            <div class="bootlegs">
                <xsl:apply-templates/>
            </div>
    </xsl:template>

    <xsl:template match="AlbumSort">
        <table>
            <tr>
                <td class="cover">
                    <img width="120" height="120" alt="No cover found!">
                        <xsl:attribute name="src">
                            <xsl:value-of select="Cover"/>
                        </xsl:attribute>
                    </img>
                </td>
                <td>
                    <p class="bootleg"><xsl:value-of select="./Date"/></p>
                    <p class="bootleg">
                        <xsl:value-of select="./Location"/>
                        <xsl:if test="./Country!='United States'">
                            <xsl:value-of select="concat(', ',./Country)"/>
                        </xsl:if>
                    </p>
                    <p class="bootleg"><xsl:value-of select="./Tour"/></p>
                </td>
            </tr>
        </table>
        <xsl:apply-templates select="Disc"/>
    </xsl:template>

    <xsl:template match="Disc">
        <h4>CD <xsl:value-of select="@id"/></h4>
        <ol>
            <xsl:apply-templates/>
        </ol>
    </xsl:template>

    <xsl:template match="Track">
        <li>
            <p class="left">
                <xsl:value-of select="."/>
            </p>
            <p class="right">
                <xsl:value-of select="@length"/>
            </p>
        </li>
    </xsl:template>

</xsl:stylesheet>
